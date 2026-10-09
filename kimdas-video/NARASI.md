# Narasi video ta'ziyah STM KIMDAS (untuk ElevenLabs)

Durasi video 2:51. Ada 16 potongan narasi. Setiap potongan punya jam mulai yang sudah pas dengan adegannya.

Penulisan sengaja disesuaikan supaya ElevenLabs melafalkannya dengan benar:
- "STM" ditulis **"Es Te Em"**, "KIMDAS" ditulis **"Kimdas"**.
- Angka ditulis dengan huruf ("lima belas", bukan "15").
- Tanda "..." memberi jeda singkat.

## Saran pengaturan ElevenLabs

- Model: **Eleven Multilingual v2**, bahasa Indonesia
- Suara: laki-laki, tenang dan hangat (cari "calm", "narrator", atau "warm")
- Stability sekitar 55%, Similarity sekitar 75%, Style 0–10%, Speed 0.9
- **Buat per potongan** (16 file), simpan sebagai `narasi/01.mp3` … `narasi/16.mp3`, lalu jalankan `python3 narasi.py`. Skrip ini menaruh tiap potongan di jam mulainya dan memperpanjang adegan yang narasinya lebih panjang. Jam mulai di tabel di bawah adalah jam versi asli 2:51.

## Naskah per potongan

| # | Mulai | Adegan di layar | Narasi |
|---|---|---|---|
| 1 | 00:01 | Layar kunci HP pengurus, ada pesan masuk dari Rizki | Subuh itu, sebuah pesan masuk ke HP pengurus. Kabar duka... datang tanpa aba-aba. |
| 2 | 00:10 | Rumah duka sepi | Pagi itu, tenda sudah berdiri. Kursi sudah disusun. Tapi yang datang... hanya beberapa orang. Bukan karena tidak peduli. Kabar datang mendadak, semua punya kesibukan, dan masing-masing mengira, pasti sudah banyak yang datang. |
| 3 | 00:25 | Logo + pertanyaan | Bagaimana jika kita saling menjaga... tanpa menambah beban siapa pun? |
| 4 | 00:31 | HP Pak Rahman mengirim lokasi | Caranya sederhana. Setiap anggota cukup sekali mengirim lokasi rumahnya lewat WhatsApp, ke nomor Es Te Em Kimdas. Data ini hanya untuk pengurus, dan tidak dibagikan ke anggota lain. |
| 5 | 00:47 | Titik-titik muncul di peta | Setiap lokasi menjadi satu titik di peta anggota, yang hanya bisa dibuka oleh pengurus. |
| 6 | 00:57 | Rumah duka ditandai, 15 anggota terdekat dipilih | Saat ada kabar duka, pengurus menandai rumah duka. Lalu sistem memilih lima belas anggota yang rumahnya paling dekat. Kabar duka tetap dikirim ke semua anggota. |
| 7 | 01:11 | HP Pak Rahman menerima permintaan khusus | Lima belas anggota ini menerima pesan khusus. Sebuah permintaan pribadi, bukan pengumuman. Cukup balas satu jika hadir hari ini, dua jika besok, atau tiga jika berhalangan. |
| 8 | 01:27 | Balasan masuk di peta | Satu per satu menjawab. Jika yang siap hadir belum cukup, sistem mengundang lima anggota berikutnya. Tidak ada denda, tidak ada paksaan. |
| 9 | 01:40 | HP Rizki menerima kabar | Keluarga pun dikabari. Insya Allah, dua belas anggota akan hadir menshalatkan almarhum. |
| 10 | 01:52 | Pengingat, anggota bergerak ke rumah duka | Menjelang shalat jenazah, satu pesan pengingat dikirim, lengkap dengan lokasi. Lalu... mereka berdatangan. |
| 11 | 02:02 | Rumah duka penuh | Tenda yang sama. Kursi yang sama. Kali ini... hampir tak ada yang kosong. |
| 12 | 02:11 | HP Pak Rahman menerima ucapan terima kasih | Setiap anggota yang hadir menerima ucapan terima kasih. |
| 13 | 02:17 | HP Rizki mengirim pesan ke STM | Dan sore harinya, sebuah pesan datang dari keluarga almarhum. |
| 14 | 02:26 | Kalimat penutup | Lima belas menit kehadiran kita... mungkin itulah yang paling lama mereka ingat. |
| 15 | 02:35 | Wakaf lahan pemakaman | Dan kelak, insya Allah, ada sepetak tanah yang dekat... untuk kita semua. |
| 16 | 02:43 | Logo + ajakan | Kirim lokasi rumah Anda ke nomor WhatsApp Es Te Em Kimdas. Cukup sekali. |

Setelah potongan 13 sengaja tidak ada narasi selama sekitar 7 detik. Biarkan penonton membaca sendiri pesan Rizki. Bagian ini justru paling menyentuh kalau dibiarkan hening.

## Versi satu file (kalau ingin sekali generate)

Tag `<break>` dibaca sebagai jeda oleh model Multilingual v2. Hasilnya tetap perlu digeser sedikit di editor supaya pas dengan adegan.

```
Subuh itu, sebuah pesan masuk ke HP pengurus. Kabar duka... datang tanpa aba-aba. <break time="2.5s" />
Pagi itu, tenda sudah berdiri. Kursi sudah disusun. Tapi yang datang... hanya beberapa orang. Bukan karena tidak peduli. Kabar datang mendadak, semua punya kesibukan, dan masing-masing mengira, pasti sudah banyak yang datang. <break time="1.0s" />
Bagaimana jika kita saling menjaga... tanpa menambah beban siapa pun? <break time="1.0s" />
Caranya sederhana. Setiap anggota cukup sekali mengirim lokasi rumahnya lewat WhatsApp, ke nomor Es Te Em Kimdas. Data ini hanya untuk pengurus, dan tidak dibagikan ke anggota lain. <break time="2.0s" />
Setiap lokasi menjadi satu titik di peta anggota, yang hanya bisa dibuka oleh pengurus. <break time="2.5s" />
Saat ada kabar duka, pengurus menandai rumah duka. Lalu sistem memilih lima belas anggota yang rumahnya paling dekat. Kabar duka tetap dikirim ke semua anggota. <break time="2.0s" />
Lima belas anggota ini menerima pesan khusus. Sebuah permintaan pribadi, bukan pengumuman. Cukup balas satu jika hadir hari ini, dua jika besok, atau tiga jika berhalangan. <break time="2.0s" />
Satu per satu menjawab. Jika yang siap hadir belum cukup, sistem mengundang lima anggota berikutnya. Tidak ada denda, tidak ada paksaan. <break time="2.5s" />
Keluarga pun dikabari. Insya Allah, dua belas anggota akan hadir menshalatkan almarhum. <break time="3.0s" />
Menjelang shalat jenazah, satu pesan pengingat dikirim, lengkap dengan lokasi. Lalu... mereka berdatangan. <break time="3.0s" />
Tenda yang sama. Kursi yang sama. Kali ini... hampir tak ada yang kosong. <break time="2.5s" />
Setiap anggota yang hadir menerima ucapan terima kasih. <break time="3.0s" />
Dan sore harinya, sebuah pesan datang dari keluarga almarhum. <break time="3.0s" />
Lima belas menit kehadiran kita... mungkin itulah yang paling lama mereka ingat. <break time="3.0s" />
Dan kelak, insya Allah, ada sepetak tanah yang dekat... untuk kita semua. <break time="2.5s" />
Kirim lokasi rumah Anda ke nomor WhatsApp Es Te Em Kimdas. Cukup sekali.
```

Batas jeda di ElevenLabs maksimal 3 detik per tag. Jeda yang lebih panjang (setelah potongan 13) diatur di editor video.
