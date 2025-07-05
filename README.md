Instagram Cupit Series
Sebuah proyek aplikasi web sederhana untuk digital matchmaking yang dirancang untuk pengunjung coffee shop. Aplikasi ini memungkinkan pengunjung untuk menemukan pasangan potensial berdasarkan kriteria tertentu, menciptakan pengalaman interaksi yang unik dan menyenangkan.

Deskripsi Singkat
"Instagram Cupit Series" adalah platform perjodohan digital ringan yang diimplementasikan di lingkungan coffee shop. Barista dapat membuat kode OTP yang diberikan kepada pelanggan. Pelanggan yang ingin berpartisipasi akan memasukkan OTP tersebut dan mengisi form singkat tentang username Instagram, gender, dan rentang usia mereka. Aplikasi kemudian akan mencocokkan mereka dengan pengguna lain berdasarkan preferensi gender berlawanan dan rentang usia yang sama.

Fitur Utama
Sisi Admin (Barista):

Generasi Kode OTP unik yang berlaku singkat (5 menit).

Melihat OTP yang telah dibuat.

Sisi Pengguna (Customer):

Halaman input OTP untuk verifikasi akses.

Form multi-step untuk mengumpulkan data: username Instagram, gender, dan rentang usia.

Tampilan hasil pairing dengan daftar username Instagram yang cocok.

Logika Pairing:

Mencocokkan pengguna berdasarkan gender berlawanan dan rentang usia yang sama.

Memastikan pengguna tidak dicocokkan dengan dirinya sendiri.

Cara Menjalankan Proyek
Ikuti langkah-langkah di bawah untuk mengatur dan menjalankan aplikasi ini:

Clone Repository (jika ada) atau Buat Struktur Proyek:
Pastikan Anda memiliki struktur folder seperti yang sudah dibahas.

Install Dependencies:
Buka terminal atau CMD, navigasikan ke folder proyek Anda (instagram-cupit-series/), lalu jalankan perintah berikut:

pip install -r requirements.txt

Siapkan Database MySQL:

Pastikan server MySQL Anda berjalan.

Buat database baru di MySQL dengan nama cupit_series_db. Anda bisa menggunakan MySQL Workbench, phpMyAdmin, atau konsol MySQL. Contoh perintah SQL:

CREATE DATABASE cupit_series_db;

Edit database.py: Buka file database.py dan perbarui detail koneksi MySQL ( user, password, host) sesuai dengan konfigurasi server MySQL Anda.

Inisialisasi Tabel Database:
Setelah mengkonfigurasi database.py, jalankan skrip ini satu kali untuk membuat tabel otps dan users:

python database.py

Anda akan melihat pesan konfirmasi jika tabel berhasil dibuat.

Jalankan Aplikasi Flask:
Di terminal atau CMD yang sama (masih di folder utama proyek instagram-cupit-series/), jalankan aplikasi Flask:

python app.py

Link Penting Setelah Aplikasi Berjalan
Halaman Admin: http://127.0.0.1:5000/admin (untuk barista membuat OTP)

Halaman Pengguna: http://127.0.0.1:5000/ (untuk pelanggan memasukkan OTP dan mengisi form)