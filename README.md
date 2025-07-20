Modul A - Grafika Komputer 2D 🎨
Proyek ini merupakan bagian dari tugas Modul A dalam mata kuliah Grafika Komputer, yang menggunakan PyOpenGL untuk membuat dan memanipulasi objek 2D dengan berbagai fitur grafika.

🖼️ Fitur Utama
✏️ Gambar objek 2D:
Titik
Garis
Persegi panjang
Elips
📐 Transformasi objek:
Translasi (t)
Rotasi (o)
Skala (s)
🔳 Clipping Window:
Gambar jendela clipping
Clipping otomatis untuk garis, persegi, dan elips
Objek di dalam window diberi warna hijau
Gerakkan window dengan panah ← ↑ → ↓
Resize window dengan [ dan ]
🖱️ Interaksi Mouse:
Klik untuk menggambar
Drag untuk membuat garis/objek
🎨 Warna objek:
r = merah
g = hijau
b = biru
🔍 Pemilihan Objek:
Mode seleksi dengan v
Pilih objek dengan klik
Gunakan n untuk menelusuri objek
🕹️ Kontrol Keyboard
Tombol	Fungsi
1	Gambar titik
2	Gambar garis
3	Gambar persegi panjang
4	Gambar elips
w	Gambar clipping window
v	Mode seleksi
r/g/b	Pilih warna
+/-	Ubah ketebalan garis
t/o/s	Mode transformasi (translasi/rotasi/skala)
m	Terapkan transformasi pada objek terpilih
[ ]	Resize clipping window
Panah	Gerakkan clipping window
c	Hapus clipping window
🚀 Cara Menjalankan
Aktifkan environment (jika ada):
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac
pip install PyOpenGL PyOpenGL_accelerate

python main.py

python -m venv .venv


Modul B - Objek 3D 📦 (Three.js)
Proyek ini merupakan bagian dari Modul B pada mata kuliah Grafika Komputer, yang bertujuan untuk memperkenalkan dasar-dasar visualisasi objek 3D di dalam browser menggunakan Three.js.

🌐 Teknologi yang Digunakan
Three.js (CDN)
HTML5 + JavaScript
WebGL melalui WebGLRenderer
🧱 Fitur Interaktif
🎥 Kamera perspektif (gluPerspective)
🎯 Kamera menghadap ke pusat objek (gluLookAt)
💡 Pencahayaan ambient & directional (dapat dimatikan atau diredam)
🔄 Transformasi objek 3D:
Rotasi (r, s)
Translasi (panah keyboard)
Skala (z, double click)
🔍 Zoom kamera (+, -)
♻️ Reset posisi awal (p)
🕹️ Kontrol
Tombol	Fungsi
r	Rotasi sumbu Y (tahan)
s	Rotasi sumbu X (tahan)
p	Reset posisi, rotasi, dan skala
z	Perkecil objek
+ / =	Zoom in kamera
-	Zoom out kamera
l	Sembunyikan/aktifkan lampu
k	Redupkan / normalkan pencahayaan
⬅️ ⬆️ ➡️ ⬇️	Translasi objek
Double Click	Perbesar objek
🚀 Cara Menjalankan
Pastikan kamu memiliki browser modern (Chrome, Edge, Firefox).
Buka file index.html langsung di browser, atau gunakan live server seperti:
npx live-server
