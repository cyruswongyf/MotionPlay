import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


class PoseLandmarker:
    def __init__(self, model_path='models/pose_landmarker.task'):
        self.pose_result = None
        self.pose_landmarker = None
        self._initialize_landmarker(model_path)

    def _initialize_landmarker(self, model_path):
        base_opt_pose = python.BaseOptions(model_asset_path=model_path)

        pose_options = vision.PoseLandmarkerOptions(
            base_options=base_opt_pose,
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self._pose_callback)

        self.pose_landmarker = vision.PoseLandmarker.create_from_options(pose_options)

    def _pose_callback(self, result, image, timestamp):
        self.pose_result = result

    def detect_async(self, frame, timestamp_ms):
        if frame is not None:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            self.pose_landmarker.detect_async(mp_image, timestamp_ms)

    def draw_landmarks_on_frame(self, frame):
        if frame is None or self.pose_result is None:
            return frame

        # Convert BGR to RGB for drawing
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        annotated_image = np.copy(rgb_image)
        pose_landmarks_list = self.pose_result.pose_landmarks

        # Loop through the detected poses to visualize
        if pose_landmarks_list:
            for idx in range(len(pose_landmarks_list)):
                pose_landmarks = pose_landmarks_list[idx]

                # Draw the pose landmarks
                pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                pose_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z)
                    for landmark in pose_landmarks
                ])
                solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    pose_landmarks_proto,
                    solutions.pose.POSE_CONNECTIONS,
                    solutions.drawing_styles.get_default_pose_landmarks_style())

        # Convert back to BGR for OpenCV
        annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        return annotated_image_bgr

    def get_landmark_data(self):
        return self.pose_result

    def release(self):
        if self.pose_landmarker:
            self.pose_landmarker.close()
