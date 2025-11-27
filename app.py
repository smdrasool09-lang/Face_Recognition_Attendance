# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition, numpy as np, cv2, base64, os, platform, json

app = Flask(__name__)
CORS(app)

# Load face data
try:
    data = np.load("face_data.npz", allow_pickle=True)
    known_face_encodings = list(data["encodings"])
    known_face_names = list(data["names"])
    print("✅ Loaded faces for:", ", ".join(sorted(set(known_face_names))))
except Exception as e:
    print("⚠ Error loading face data:", e)
    known_face_encodings, known_face_names = [], []

# Load student info map
info_path = "student_info.json"
student_info = {}
if os.path.exists(info_path):
    try:
        with open(info_path, "r", encoding="utf-8") as f:
            student_info = json.load(f)
        print("✅ Loaded student info for:", ", ".join(student_info.keys()))
    except Exception as e:
        print("⚠ Error loading student_info.json:", e)

def lookup_info(name: str):
    # Exact match first, then case-insensitive fallback
    if name in student_info:
        return student_info[name]
    for k in student_info.keys():
        if k.strip().lower() == name.strip().lower():
            return student_info[k]
    return {"section": "Unknown", "department": "Unknown"}

@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        image_data = request.json["image"]

        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Invalid image"})

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        if not face_encodings:
            return jsonify({"status": "no_face"})

        # Find best match by average distance per name
        name = "Unknown"
        best_score = 1.0
        if known_face_encodings:
            person_scores = {}
            for enc, nm in zip(known_face_encodings, known_face_names):
                dists = face_recognition.face_distance([enc], face_encodings[0])
                person_scores.setdefault(nm, []).append(float(dists[0]))
            # pick lowest average
            for nm, dlist in person_scores.items():
                avg = float(np.mean(dlist))
                if avg < best_score:
                    best_score, name = avg, nm

        if best_score < 0.5:
            info = lookup_info(name)
            section = info.get("section", "Unknown")
            department = info.get("department", "Unknown")

            # Call Java to store in MySQL
            sep = ";" if platform.system() == "Windows" else ":"
            cmd = f'cd ../attendance && java -cp ".{sep}../bin{sep}../mysql-connector.jar" attendance.AttendanceRecorder "{name}" "{section}" "{department}"'
            os.system(cmd)

            return jsonify({"status": "recognized", "name": name, "section": section, "department": department})
        else:
            return jsonify({"status": "detected", "name": "Unknown"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)