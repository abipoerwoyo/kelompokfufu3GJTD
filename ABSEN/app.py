from flask import Flask, render_template, request, redirect, url_for
from face_recognition_util import load_known_faces, recognize_face
from PIL import Image
import datetime
import base64
from io import BytesIO
import pyodbc

app = Flask(__name__)

# Koneksi ke database SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=LAPTOP-KUC4T2Q8\\SQLEXPRESS;'
    'DATABASE=AbsensiDB;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# Fungsi untuk menghapus data lama dan reset ID
def clear_absensi_data():
    cursor.execute("DELETE FROM Absensi")
    cursor.execute("DBCC CHECKIDENT ('Absensi', RESEED, 0)")  # Reset ID agar mulai dari 1
    conn.commit()
    print("[INFO] Data Absensi telah dihapus dan ID disetel ulang.")

# Jalankan penghapusan data & reset ID saat startup
clear_absensi_data()

# Load wajah yang dikenali
known_encodings, known_names = load_known_faces()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/absen', methods=['GET', 'POST'])
def absen():
    if request.method == 'POST':
        image_data = request.form.get("image_data")
        if not image_data:
            return render_template("absen.html", error="Data gambar tidak ditemukan")

        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_bytes))
        img_path = "static/captured.jpg"
        image.save(img_path)

        nama = recognize_face(img_path, known_encodings, known_names)
        if nama and "tidak" not in nama.lower():
            waktu = datetime.datetime.now()

            # Cari NIM berdasarkan nama
            cursor.execute("SELECT nim FROM Mahasiswa WHERE nama = ?", nama)
            result = cursor.fetchone()

            if result:
                nim = result.nim
                cursor.execute("INSERT INTO Absensi (nama, nim, waktu) VALUES (?, ?, ?)", nama, nim, waktu)
                conn.commit()
                return redirect(url_for('rekap'))
            else:
                return render_template("absen.html", error="NIM tidak ditemukan untuk mahasiswa: " + nama)

        else:
            return render_template("absen.html", error="Wajah tidak dikenali")

    return render_template("absen.html")

@app.route('/rekap')
def rekap():
    cursor.execute("SELECT nama, nim, waktu FROM Absensi ORDER BY waktu ASC")
    rows = cursor.fetchall()
    data = []
    for i, row in enumerate(rows, start=1):
        data.append({
            "no": i,
            "nama": row.nama,
            "nim": row.nim,
            "waktu": row.waktu.strftime("%d-%m-%Y %H:%M:%S")
        })
    return render_template("rekap.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)
