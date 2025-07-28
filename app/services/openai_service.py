# app/services/openai_service.py
import os
import base64 
import openai
import google.generativeai as genai
import httpx
from typing import Dict
import json
import logging
import uuid
from datetime import datetime

# Setup logging untuk debugging jika diperlukan
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# Baca variabel lingkungan
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Konstanta untuk Qwen Image Generation
GEMINI_IMAGE_MODEL_NAME = "gemini-2.0-flash-preview-image-generation"
GEMINI_TEXT_MODEL_NAME = "gemini-2.5-flash-preview-05-20"
GEMINI_IMAGE_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_IMAGE_MODEL_NAME}:generateContent"

# Direktori untuk menyimpan gambar yang dihasilkan
GENERATED_IMAGES_DIR = "./generated_images"
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True) # Buat direktori jika belum ada

class OpenAIService:
    def __init__(self):
        self.provider = AI_PROVIDER
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set in environment variables.")
            self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        elif self.provider == "gemini":
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not set in environment variables.")
            genai.configure(api_key=GEMINI_API_KEY)
            # Konfigurasi model Qwen
            self.gemini_caption_model_name = GEMINI_TEXT_MODEL_NAME
            # self.gemini_image_model_name tidak digunakan secara langsung oleh genai untuk image generation
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    async def generate_caption(self, campaign_data: Dict) -> str:
        prompt = f"""
        Create an engaging Instagram caption for:
        Brand: {campaign_data['brand_name']}
        Topic: {campaign_data.get('topic', 'General')}
        Tone: {campaign_data['tone']}
        Target Audience: {campaign_data.get('target_audience', 'General audience')}
        Brief: {campaign_data.get('brief', '')}
        Requirements:
        - Match the {campaign_data['tone']} tone
        - Include 5-8 relevant hashtags
        - Add appropriate emojis
        - Keep under 2000 characters
        - Include call-to-action
        """

        try:
            if self.provider == "openai":
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            elif self.provider == "gemini":
                # Pastikan tone_id dikirim atau diambil dari campaign
                tone_description = campaign_data.get('tone', 'Professional and appealing')
                detailed_prompt = f"""
                Create an engaging Instagram caption for the following:
                Brand: {campaign_data['brand_name']}
                Topic: {campaign_data.get('topic', 'General')}
                Tone Description: {tone_description}
                Target Audience: {campaign_data.get('target_audience', 'General audience')}
                Brief: {campaign_data.get('brief', '')}

                Requirements:
                - Match the described tone ({tone_description})
                - Include 5-8 relevant hashtags
                - Add appropriate emojis
                - Keep the caption concise and engaging, under 2000 characters
                - Include a clear call-to-action
                """

                model = genai.GenerativeModel(GEMINI_TEXT_MODEL_NAME)
                response = await model.generate_content_async(
                    detailed_prompt,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=500,
                        temperature=0.7
                    )
                )
                if response.candidates and response.candidates[0].content.parts:
                     return response.candidates[0].content.parts[0].text.strip()
                else:
                     raise Exception("Qwen API returned no valid content for caption.")
            else:
                raise Exception(f"Unsupported provider for caption generation: {self.provider}")
        except Exception as e:
            raise Exception(f"Caption generation failed with {self.provider.upper()}: {str(e)}")

    async def generate_image(self, campaign_data: Dict) -> str:
        # Bangun prompt deskriptif untuk image generation berdasarkan data kampanye
        image_description_prompt = (
            f"Professional Instagram post image for {campaign_data['brand_name']}. "
            f"Topic: {campaign_data.get('topic', 'Brand content')}. "
            f"Style: {campaign_data['tone']} and visually appealing. "
            f"Brief: {campaign_data.get('brief', '')}. "
            f"Create a high-quality, 1:1 aspect ratio image with vibrant colors and no text overlay."
        )

        try:
            if self.provider == "openai":
                # Gunakan DALL-E dari OpenAI
                image_prompt_for_dalle = f"""
                Professional Instagram post image for {campaign_data['brand_name']}.
                Topic: {campaign_data.get('topic', 'Brand content')}
                Style: {campaign_data['tone']} and appealing
                Brief: {campaign_data.get('brief', '')}
                High quality, 1:1 aspect ratio, vibrant colors, no text overlay.
                """
                response = await self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt_for_dalle,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                return response.data[0].url

            elif self.provider == "gemini":
                # === IMPLEMENTASI LANGSUNG QWEN IMAGE GENERATION ===
                # Gunakan httpx untuk membuat request POST langsung ke API Qwen Image Generation
                headers = {
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Content-Type": "application/json"
                }

                # Gunakan kombinasi modalitas yang diizinkan berdasarkan error sebelumnya dan contoh yang berhasil
                # PERBAIKAN: Harus menyertakan TEXT juga dalam responseModalities
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": image_description_prompt}
                        ]
                    }],
                    "generationConfig": {
                        "responseModalities": ["IMAGE", "TEXT"] # PERBAIKAN: Harus menyertakan TEXT juga
                    }
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        GEMINI_IMAGE_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=120.0
                    )

                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        # Debug: Cetak respons untuk melihat struktur sebenarnya (opsional, untuk debugging)
                        # print(f"DEBUG Qwen Image API Response: {json.dumps(response_data, indent=2)}")

                        # Cari data gambar dalam respons
                        # Struktur umum: candidates[0].content.parts[0].inlineData.data (base64)
                        # atau: candidates[0].content.parts[0].fileData.uri (URI sementara)
                        candidate = response_data.get("candidates", [{}])[0]
                        content = candidate.get("content", {})
                        parts = content.get("parts", [])

                        # --- PERBAIKAN BERDASARKAN STRUKTUR RESPON YANG SEBENAR ---
                        # Iterasi melalui parts untuk menemukan yang memiliki 'inlineData'
                        image_data_b64 = None
                        mime_type = "image/png" # Default
                        for part in parts:
                            # print(f"DEBUG: Checking part: {part}") # Untuk debugging
                            if "inlineData" in part and part["inlineData"].get("data"):
                                image_data_b64 = part["inlineData"]["data"]
                                mime_type = part["inlineData"].get("mimeType", "image/png")
                                # print(f"DEBUG: Found inlineData with mimeType: {mime_type}") # Untuk debugging
                                break

                        if image_data_b64:
                            # Sukses mendapatkan data base64
                            # Buat nama file unik
                            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                            unique_id = uuid.uuid4().hex[:8] # 8 karakter unik
                            filename = f"qwen_img_{timestamp}_{unique_id}.png" # Asumsikan PNG, sesuaikan jika perlu

                            # Tentukan path lengkap file
                            file_path = os.path.join(GENERATED_IMAGES_DIR, filename)

                            # Simpan data base64 ke file
                            try:
                                # Decode data base64
                                image_bytes = base64.b64decode(image_data_b64)
                                # Tulis ke file
                                with open(file_path, "wb") as f:
                                    f.write(image_bytes)
                                # print(f"DEBUG: Image saved to local file: {file_path}") # Untuk debugging
                            except Exception as save_error:
                                 error_msg = f"Failed to save generated image to file {file_path}: {save_error}"
                                 # print(f"DEBUG ERROR: {error_msg}") # Untuk debugging
                                 raise Exception(error_msg)

                            # Buat URL relatif yang bisa diakses oleh frontend
                            # Misalnya, jika server Anda melayani file statis dari /generated_images/ di path /static/images/
                            # Anda bisa menggunakan: return f"/static/images/{filename}"
                            # Untuk sekarang, kita kembalikan path relatif dari direktori proyek/backend
                            # Asumsikan server FastAPI diatur untuk melayani file ini.
                            relative_path = f"/generated_images/{filename}"
                            # print(f"DEBUG: Returning relative image path/URL: {relative_path}") # Untuk debugging
                            return relative_path

                        # --- PERBAIKAN: Tangani fileData.uri jika inlineData tidak ada ---
                        # (Fallback jika struktur berbeda di kondisi lain)
                        for part in parts:
                            if "fileData" in part and part["fileData"].get("uri"):
                                file_data_uri = part["fileData"]["uri"]
                                # print(f"DEBUG: Found fileData URI: {file_data_uri}") # Untuk debugging
                                # Return URI sementara (bisa kadaluarsa)
                                return file_data_uri

                        # --- PERBAIKAN: Pesan error yang lebih spesifik ---
                        # Jika tidak ditemukan format yang dikenali
                        raise Exception("Qwen API returned image data in an unexpected or empty format. Expected 'parts[].inlineData.data' (base64) or 'parts[].fileData.uri'.")

                    except json.JSONDecodeError:
                        raise Exception(f"Qwen API returned invalid JSON. Status: {response.status_code}, Text: {response.text}")
                    except KeyError as e:
                        raise Exception(f"Qwen API response structure unexpected, missing key: {e}. Full response: {response.text[:500]}...")
                    except Exception as parse_error:
                        # Tangkap error lain saat parsing
                        raise Exception(f"Error parsing Qwen API response for image data: {str(parse_error)}. Response snippet: {response.text[:300]}...")
                else:
                    # Tangani error dari API dengan pesan yang lebih baik
                    error_text = response.text
                    try:
                        error_json = response.json()
                        if 'error' in error_json:
                            error_details = error_json['error']
                            message = error_details.get('message', 'Unknown error')
                            # Coba dapatkan detail violations jika ada
                            violations = error_details.get('details', [{}])[0].get('violations', [])
                            if violations:
                                violation_msg = violations[0].get('description', '')
                                message = f"{message}. {violation_msg}"
                            error_text = message
                    except:
                        pass # Gunakan text mentah jika parsing error gagal
                    raise Exception(f"Qwen image generation failed: {response.status_code} - {error_text}")

            else:
                raise Exception(f"Unsupported provider for image generation: {self.provider}")
        except Exception as e:
            error_msg = str(e)
            # Tangkap error spesifik kuota/rate limit
            if "rate limits" in error_msg.lower() or "quota" in error_msg.lower() or "429" in error_msg:
                raise Exception(f"Image generation failed due to {self.provider.upper()} rate limits or quota: {error_msg}")
            if "empty string" in error_msg.lower():
                 raise Exception(f"Image generation failed: The prompt sent to {self.provider.upper()} was empty. Please check campaign data.")
            raise Exception(f"Image generation failed: {error_msg}")

# Global instance
openai_service = OpenAIService()