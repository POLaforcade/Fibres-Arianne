"""
Created on Fry May 26
@author : Laforcade
"""
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

# Modele parameters and detector object init
base_options = python.BaseOptions(model_asset_path='modeles\\mediapipe\\pose_landmarker_lite.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True)
detector = vision.PoseLandmarker.create_from_options(options)

def draw_landmarks_on_image(rgb_image, detection_result):
  """
  Draw pose detection landmarks on an image
    Args : 
        rgb_image : the image as a numpy array to draw results on
        detection_result : An array that contains the points of interest 
    Ret : 
        annotated_image : the numpy array with landmarks to show with cv2.imshow()
  """
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image

def Show_pose_person(file_path : str):
    """
    Shows a video with pose detection and landmarks
        Args : 
            file_path : the path to the video that must be computed
    """
    cap = cv2.VideoCapture(file_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = detector.detect(mp_frame)
        frame = draw_landmarks_on_image(frame, detection_result)
        cv2.imshow('Video', frame)
        if cv2.waitKey(16) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return