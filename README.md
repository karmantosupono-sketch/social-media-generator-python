# Social Media Content Generator - Backend

Backend untuk sistem yang dapat menghasilkan konten media sosial (caption & gambar) secara batch menggunakan AI (OpenAI atau Google Qwen).

## 🎯 Fitur Utama

* **Autentikasi JWT**: Login pengguna aman.
* **Manajemen Kampanye**: Buat dan kelola kampanye branding Anda.
* **Generasi Batch (Inti)**: Hasilkan 10-100 postingan Instagram secara simultan.
* **Integrasi AI**: Dukungan untuk OpenAI (GPT, DALL-E) dan Google Qwen (Gemini).
* **Pelacakan Progres**: Pantau status dan hasil batch secara real-time.
* **Performa Tinggi**: Dirancang untuk memenuhi target kecepatan ketat.

## 🚀 Teknologi yang Digunakan

* **Bahasa**: Python 3.9+
* **Framework**: FastAPI
* **Database**: PostgreSQL
* **ORM & Migrasi**: SQLAlchemy 2.x, Alembic
* **AI**: OpenAI Python SDK, Google Generative AI SDK, `httpx`
* **Keamanan**: Bcrypt, python-jose

## 📦 Prasyarat

Sebelum menjalankan backend, pastikan Anda telah menginstal:

* **Python 3.9 - 3.11**
* **PostgreSQL** (dengan ekstensi `uuid-ossp` aktif)
* **Git** (untuk kloning repositori)

## 🛠️ Setup & Instalasi

Ikuti langkah-langkah berikut untuk menyiapkan lingkungan pengembangan:

1. **Klon Repositori:**

   ```bash
   git clone <URL_REPOSITORI_ANDA>
   cd social-media-generator-python
   ```

2. **Buat dan Aktifkan Virtual Environment:** Menggunakan virtual environment sangat disarankan untuk mengisolasi dependensi proyek ini.

   ```bash
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows (Command Prompt)
   python -m venv venv
   venv\Scripts\activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Instal Dependensi:** Semua dependensi yang diperlukan sudah tercantum dalam `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

4. **Siapkan Database PostgreSQL:**

   * Jalankan service PostgreSQL di sistem Anda.
   * Buat database baru untuk aplikasi ini (misalnya, `social_media_db`).

     ```sql
     CREATE DATABASE social_media_db;
     ```
   * Pastikan ekstensi `uuid-ossp` diaktifkan di database tersebut.

     ```sql
     CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
     ```

5. **Konfigurasi File **\`\`**:** Buat file bernama `.env` di direktori `backend` dan isi dengan konfigurasi Anda. Gunakan `.env.example` sebagai template. Contoh isi `.env`:

   ```env
   # Format: postgresql://[user[:password]@][host][:port][/database]
   DATABASE_URL=postgresql://postgres:password_anda@localhost/social_media_db

   # Pilih penyedia AI: 'openai' atau 'gemini'
   AI_PROVIDER=openai

   # Dapatkan API Key dari platform yang sesuai
   OPENAI_API_KEY=sk-...your_openai_api_key...
   GEMINI_API_KEY=AIzaSy...your_gemini_api_key...

   # Secret Key untuk JWT (buat yang sangat panjang dan acak)
   # Contoh membuat key: openssl rand -hex 32
   SECRET_KEY=kunci_rahasia_yang_sangat_panjang_dan_acak_di_sini
   ```

6. **Jalankan Migrasi Database:** Gunakan Alembic untuk membuat tabel dan (opsional) mengisi data awal.

   ```bash
   # Buat tabel berdasarkan model
   alembic upgrade head
   ```

## ▶️ Menjalankan Server

Di dalam direktori `backend` dan dengan virtual environment aktif, jalankan server pengembangan:

```bash
uvicorn app.main:app --reload
```

## 📖 Contoh Penggunaan

Berikut beberapa contoh CURL untuk memudahkan integrasi dan pengujian:

### 1. Login (Mendapatkan JWT Token)

```bash
curl -X POST \
  'http://localhost:8000/api/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

### 2. Buat Kampanye Baru

```bash
curl -X POST \
  'http://localhost:8000/api/campaigns/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN_ANDA>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Test Campaign",
    "brand_name": "My Awesome Brand",
    "description": "A test campaign for social media posts",
    "target_audience": "Tech enthusiasts",
    "tone_id": "friendly"
  }'
```

### 3. Generate Batch Posting

```bash
curl -X 'POST' \
  'http://localhost:8000/api/batch-jobs/campaigns/016c7c05-c582-4fd7-a87f-f6ca5b2d4824/generate-batch' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN_ANDA>' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "First Batch Test",
  "posts": [
    {
      "title": "Innovative Gadget Review",
      "topic": "Product Review",
      "brief": "Review our latest tech gadget with pros, cons, and first impressions.",
      "generate_caption": true,
      "generate_image": true
    }
  ]
}'
```

> **Catatan:** Ganti `<JWT_TOKEN_ANDA>` dengan token yang diperoleh dari endpoint login.

---

Dengan contoh di atas, Anda dapat langsung mencoba berbagai fitur utama sistem dan mempermudah proses integrasi pada aplikasi klien atau skrip pengujian.
