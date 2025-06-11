import face_recognition
import os
import numpy as np
import pickle
import hashlib

ENCODING_FILE = "face_encodings.pkl"
HASH_FILE = "face_dataset.hash"

def calculate_dataset_hash(path="known_faces"):
    """Menghitung hash dari isi folder untuk mendeteksi perubahan"""
    hash_md5 = hashlib.md5()
    for filename in sorted(os.listdir(path)):
        if filename.lower().endswith((".jpg", ".png")):
            filepath = os.path.join(path, filename)
            hash_md5.update(filename.encode('utf-8'))
            with open(filepath, "rb") as f:
                hash_md5.update(f.read())
    return hash_md5.hexdigest()

def load_known_faces(path="known_faces"):
    current_hash = calculate_dataset_hash(path)

    # Cek apakah encoding dan hash sebelumnya ada
    if os.path.exists(ENCODING_FILE) and os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            saved_hash = f.read()
        if saved_hash == current_hash:
            print("[INFO] Dataset belum berubah. Memuat dari cache...")
            with open(ENCODING_FILE, "rb") as f:
                return pickle.load(f)

    print("[INFO] Dataset berubah atau pertama kali. Melakukan encoding ulang...")
    known_face_encodings = []
    known_face_names = []

    for file in os.listdir(path):
        if file.lower().endswith((".jpg", ".png")):
            filepath = os.path.join(path, file)
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_face_encodings.append(encodings[0])
                filename = os.path.splitext(file)[0]
                name = filename.split('_')[0]
                known_face_names.append(name)
            else:
                print(f"[WARNING] Tidak ada wajah ditemukan di file: {file}")

    # Simpan encoding & hash ke file
    with open(ENCODING_FILE, "wb") as f:
        pickle.dump((known_face_encodings, known_face_names), f)
    with open(HASH_FILE, "w") as f:
        f.write(current_hash)
    print("[INFO] Cache encoding wajah dan hash dataset diperbarui.")

    return known_face_encodings, known_face_names

def recognize_face(image_path, known_encodings, known_names):
    import face_recognition
    import numpy as np

    unknown_image = face_recognition.load_image_file(image_path)
    unknown_encodings = face_recognition.face_encodings(unknown_image)

    if not unknown_encodings:
        return "Tidak ada wajah terdeteksi"

    results = face_recognition.compare_faces(known_encodings, unknown_encodings[0])
    distances = face_recognition.face_distance(known_encodings, unknown_encodings[0])

    if True in results:
        best_match_index = np.argmin(distances)
        return known_names[best_match_index]
    else:
        return "Wajah tidak dikenal"