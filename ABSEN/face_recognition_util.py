import face_recognition
import os
import cv2
import numpy as np

def load_known_faces(path="known_faces"):
    known_face_encodings = []
    known_face_names = []

    for file in os.listdir(path):
        if file.lower().endswith((".jpg", ".png")):
            filepath = os.path.join(path, file)
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_face_encodings.append(encodings[0])

                # Ambil nama sebelum karakter '_' atau ambil semua jika tidak ada '_'
                filename = os.path.splitext(file)[0]
                name = filename.split('_')[0]
                known_face_names.append(name)
            else:
                print(f"[WARNING] Tidak ada wajah ditemukan di file: {file}")

    return known_face_encodings, known_face_names

def recognize_face(image_path, known_encodings, known_names):
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
