# save_faces.py
import cv2, face_recognition, numpy as np, os, json

# Load face data
known_encodings, known_names = [], []
if os.path.exists("face_data.npz"):
    try:
        data = np.load("face_data.npz", allow_pickle=True)
        known_encodings = list(data["encodings"])
        known_names = list(data["names"])
    except Exception as e:
        print("⚠ Could not load face_data.npz:", e)

# Load student info map
info_path = "student_info.json"
student_info = {}
if os.path.exists(info_path):
    try:
        with open(info_path, "r", encoding="utf-8") as f:
            student_info = json.load(f)
    except Exception as e:
        print("⚠ Could not load student_info.json:", e)

print(f"✅ Current dataset size: {len(known_names)}")

# Ask once
print("\n📋 Enter student details:")
name = input("Name       : ").strip()
section = input("Section    : ").strip()
department = input("Department : ").strip()

# Save info (case-insensitive key normalization)
key = name.strip()
student_info[key] = {"section": section.strip(), "department": department.strip()}
with open(info_path, "w", encoding="utf-8") as f:
    json.dump(student_info, f, indent=2, ensure_ascii=False)

# Capture face
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open camera."); exit(1)

print(f"\n🎥 Capturing face for {name}... Press 'q' or 'Esc' to finish.")
face_encodings = []

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠ Camera not returning frames."); break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encs = face_recognition.face_encodings(rgb)
    if encs:
        face_encodings.append(encs[0])
        cv2.putText(frame, "Frame captured", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Saving Face", frame)
    k = cv2.waitKey(10) & 0xFF
    if k in [ord('q'), 27]:
        break

cap.release()
cv2.destroyAllWindows()

# Save face dataset
if len(face_encodings) == 0:
    print(f"❌ No faces captured for {name}, nothing saved.")
else:
    known_encodings.extend(face_encodings)
    known_names.extend([key] * len(face_encodings))
    np.savez("face_data.npz", encodings=np.array(known_encodings), names=np.array(known_names))
    print("\n✔ Attendance marked for student")
    print(f"Name       : {name}")
    print(f"Section    : {section}")
    print(f"Department : {department}")
    print(f"🧠 {len(face_encodings)} frame(s) saved for {name}")