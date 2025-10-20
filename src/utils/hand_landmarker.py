import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


class HandLandmarker:
    def save_landmarks_to_csv(self, filename, gesture_label=None):
        """
        Save all detected hand landmarks as one row to CSV.
        gesture_label: Optional, label for this data sample.
        """
        import csv
        result = self.get_landmark_data()
        if not result or not result.hand_landmarks:
            print("No hand landmarks to save.")
            return
        rows = []
        for hand_landmarks in result.hand_landmarks:
            row = []
            for lm in hand_landmarks:
                row.extend([lm.x, lm.y, lm.z])
            if gesture_label is not None:
                row.append(gesture_label)
            rows.append(row)
        # Check if file exists to decide whether to write header
        import os
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                header = []
                for i in range(21):
                    header += [f'x{i}', f'y{i}', f'z{i}']
                if gesture_label is not None:
                    header.append('label')
                writer.writerow(header)
            writer.writerows(rows)
        print(f"Saved {len(rows)} hand(s) landmarks to {filename}")
    def __init__(self, model_path='models/hand_landmarker.task', num_hands=2):
        self.hand_result = None
        self.hand_landmarker = None
        self.num_hands = num_hands
        self._initialize_landmarker(model_path)

    def _initialize_landmarker(self, model_path):
        base_opt = python.BaseOptions(model_asset_path=model_path)

        options = vision.HandLandmarkerOptions(
            base_options=base_opt,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=self.num_hands,
            result_callback=self._hand_callback,
        )

        self.hand_landmarker = vision.HandLandmarker.create_from_options(options)

    def _hand_callback(self, result, image, timestamp):
        self.hand_result = result

    def detect_async(self, frame, timestamp_ms):
        if frame is not None:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            self.hand_landmarker.detect_async(mp_image, timestamp_ms)

    def draw_landmarks_on_frame(self, frame, color_left=(0, 255, 0), color_right=(0, 128, 255)):
        if frame is None or self.hand_result is None:
            return frame

        # Convert BGR to RGB for drawing
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        annotated = np.copy(rgb_image)


        hand_landmarks_list = self.hand_result.hand_landmarks or []
        handedness_list = self.hand_result.handedness or []

        for idx, hand_landmarks in enumerate(hand_landmarks_list):
            # Build proto for drawing utils
            lm_proto = landmark_pb2.NormalizedLandmarkList()
            lm_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
                for lm in hand_landmarks
            ])

            # Choose color by handedness if available (handle handedness as list of list)
            color = (0, 255, 0)
            label = None
            if idx < len(handedness_list):
                # handedness_list[idx] is a list of Category objects
                handedness_categories = handedness_list[idx]
                if isinstance(handedness_categories, list) and len(handedness_categories) > 0:
                    category = handedness_categories[0]
                    if hasattr(category, 'category_name'):
                        label = category.category_name
                        color = color_left if label == 'Left' else color_right

            # Draw connections and landmarks
            solutions.drawing_utils.draw_landmarks(
                annotated,
                lm_proto,
                solutions.hands.HAND_CONNECTIONS,
                solutions.drawing_styles.get_default_hand_landmarks_style(),
                solutions.drawing_styles.get_default_hand_connections_style(),
            )

            # Overlay handedness label near wrist (landmark 0)
            if label is not None:
                wrist = hand_landmarks[0]
                h, w, _ = annotated.shape
                cx, cy = int(wrist.x * w), int(wrist.y * h)
                cv2.putText(annotated, label, (cx + 6, cy - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Convert back to BGR for OpenCV
        return cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

    def get_landmark_data(self):
        return self.hand_result

    def release(self):
        if self.hand_landmarker:
            self.hand_landmarker.close()
