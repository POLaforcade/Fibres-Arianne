import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red


def visualize(image, detection_result) -> np.ndarray:
  """Draw bounding boxes on the input image and return it.
  Args:
    image: The input RGB image.
    detection_result: The list of all "Detection" entities to be visualize.
  Returns:
    Image with bounding boxes.
  """
  for detection in detection_result.detections:
    if(detection.categories[0].category_name == 'person'):
        # Draw bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = category_name + ' (' + str(probability) + ')'
        text_location = (MARGIN + bbox.origin_x,
                        MARGIN + ROW_SIZE + bbox.origin_y)
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

  return image

def detect_object(file_path : str):
    """Show a video with bounding boxes around detected person
    Args :
        file_path : path to the RGB video that msut be computed
    """
    # Open capture
    cap = cv2.VideoCapture(file_path)
    # Open model
    model_path = 'modeles\\mediapipe\\efficientdet_lite0.tflite'
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                        score_threshold=0.2)
    detector = vision.ObjectDetector.create_from_options(options)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # 1. Save orginal frame
        frame_base = frame

        # 2 Use model detection on frame
        frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = detector.detect(frame)

        # 3 display result
        annotated_image = visualize(frame_base, detection_result)
        rgb_annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        cv2.imshow("Image detection", rgb_annotated_image)

        if cv2.waitKey(16) & 0xFF == ord('q'): # Lis la video à 60 fps
            break

    cap.release()
    cv2.destroyAllWindows()