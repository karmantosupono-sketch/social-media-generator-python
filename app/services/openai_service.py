# app/services/openai_service.py (atau ganti nama menjadi ai_service.py)
import os
import openai
import google.generativeai as genai # Tambahkan import untuk Qwen
from typing import Dict, Optional

# Baca variabel lingkungan
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower() # Default ke 'openai'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
            # Anda bisa konfigurasi model default di sini
            # Misalnya, tentukan model untuk caption dan image
            self.gemini_caption_model_name = "gemini-1.5-flash" # Sesuaikan dengan model yang tersedia
            self.gemini_image_model_name = "gemini-1.5-flash" # Qwen tidak generate image secara langsung, butuh DALL-E atau tool lain
            # Untuk sementara, kita fokus pada caption dulu untuk Qwen
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
                    model="gpt-4o-mini", # Pastikan model ini tersedia dan sesuai
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            elif self.provider == "gemini":
                model = genai.GenerativeModel(self.gemini_caption_model_name)
                response = await model.generate_content_async(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=500,
                        temperature=0.7
                    )
                )
                # Tangani kemungkinan kandidat respons
                if response.candidates and response.candidates[0].content.parts:
                     return response.candidates[0].content.parts[0].text.strip()
                else:
                     # Tangani kasus jika tidak ada kandidat atau teks yang dihasilkan
                     raise Exception("Qwen API returned no valid content for caption.")
            else:
                raise Exception(f"Unsupported provider for caption generation: {self.provider}")
        except Exception as e:
            raise Exception(f"Caption generation failed with {self.provider.upper()}: {str(e)}")

    async def generate_image(self, campaign_data: Dict) -> str:
        # Qwen tidak memiliki model image generation bawaan seperti DALL-E.
        # Untuk image generation dengan Qwen, Anda biasanya perlu mengintegrasikannya
        # dengan tool lain (misalnya, memanggil DALL-E dari dalam prompt Qwen, atau
        # menggunakan layanan pihak ketiga lainnya).
        # Untuk kesederhanaan sekarang, kita tetap gunakan DALL-E jika provider adalah 'gemini'
        # atau buat logika terpisah jika diperlukan. Namun, dokumen asli hanya menggunakan DALL-E.
        # Jadi, kita bisa memutuskan untuk selalu gunakan DALL-E untuk image, terlepas dari provider caption,
        # atau membuat error jika mencoba generate image dengan Qwen.

        # Opsi 1: Selalu gunakan DALL-E untuk image (paling sederhana)
        # if not OPENAI_API_KEY:
        #     raise Exception("OPENAI_API_KEY is required for image generation (DALL-E).")
        # dalle_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

        # Opsi 2: Error jika mencoba generate image dengan Qwen
        if self.provider == "gemini":
            raise Exception("Image generation is not supported with the Qwen provider. Please use 'openai' for image generation or implement a custom image generation tool.")

        image_prompt = f"""
        Professional Instagram post image for {campaign_data['brand_name']}.
        Topic: {campaign_data.get('topic', 'Brand content')}
        Style: {campaign_data['tone']} and appealing
        Brief: {campaign_data.get('brief', '')}
        High quality, 1:1 aspect ratio, vibrant colors, no text overlay.
        """
        try:
            # Untuk Opsi 1, gunakan `dalle_client` di sini
            # response = await dalle_client.images.generate(
            # Opsi 2 (saat ini aktif): Gunakan client OpenAI utama jika provider awalnya openai
            if self.provider != "openai":
                # Jika provider bukan openai tapi mencoba generate image, error sudah dilempar sebelumnya.
                # Tapi jika ingin memaksa gunakan OpenAI untuk image meski caption pakai Qwen:
                if not OPENAI_API_KEY:
                     raise Exception("OPENAI_API_KEY is required for image generation (DALL-E).")
                dalle_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
                response = await dalle_client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
            else:
                # Jika provider adalah openai
                response = await self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
            return response.data[0].url
        except Exception as e:
            # Tangani error secara spesifik jika diperlukan
            raise Exception(f"Image generation failed: {str(e)}")

# Global instance
openai_service = OpenAIService()