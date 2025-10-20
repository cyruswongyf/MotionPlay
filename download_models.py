import urllib.request, os

urls = {
    "models/pose_landmarker.task" :
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task",
    "models/gesture_recognizer.task" :
        "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task",
    "models/hand_landmarker.task":
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
}

for file_name, url in urls.items():
    if os.path.exists(file_name):
        print(f"{file_name} exists")
        continue
    print(f"Installing {file_name} ...")
    urllib.request.urlretrieve(url, file_name)
    print("Complete Install")