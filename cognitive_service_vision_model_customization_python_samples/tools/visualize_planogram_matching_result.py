from typing import Dict, Any

import cv2
import numpy as np


def _draw_dashed_rect(image: np.ndarray, pt1: tuple, pt2: tuple, color: tuple, thickness: int, d: int) -> None:
    # Draw the dashed line in four directions
    for i in range(0, np.abs(pt2[0]-pt1[0]), d*2):
        cv2.line(image, (pt1[0]+i, pt1[1]), (pt1[0]+i+d, pt1[1]), color, thickness)
    for i in range(0, np.abs(pt2[1]-pt1[1]), d*2):
        cv2.line(image, (pt2[0], pt1[1]+i), (pt2[0], pt1[1]+i+d), color, thickness)
    for i in range(0, np.abs(pt2[0]-pt1[0]), d*2):
        cv2.line(image, (pt1[0]+i, pt2[1]), (pt1[0]+i+d, pt2[1]), color, thickness)
    for i in range(0, np.abs(pt2[1]-pt1[1]), d*2):
        cv2.line(image, (pt1[0], pt1[1]+i), (pt1[0], pt1[1]+i+d), color, thickness)


def visualize_matching_result(img: np.ndarray, detected_objects: Dict[str, Any], planogram: Dict[str, Any]) -> np.ndarray:
    # Image dimensions
    img_height, img_width = img.shape[:2]

    # Create a dictionary of detected objects by positionId for easy lookup
    detected_objects_dict = {obj['positionId']: obj for obj in detected_objects['matchingResultPerPosition']}

    for position in planogram["Positions"]:
        # Normalize planogram position and convert to pixel coordinates
        x = int((position["X"] / planogram["Width"]) * img_width)
        y = int((position["Y"] / planogram["Height"]) * img_height)

        # Use the product dimensions for the width and height of the box
        # Note: This assumes that the product dimensions are also relative to the planogram's width and height
        product = next((p for p in planogram["Products"] if p["Id"] == position["ProductId"]), None)
        if product is not None:
            w = int((product["W"] / planogram["Width"]) * img_width)
            h = int((product["H"] / planogram["Height"]) * img_height)

            # Default planogram position color is green
            color = (0, 255, 0)  # Green

            # If this positionId matches a detected object with a 'gap' tag, change box color to red
            detected_obj = detected_objects_dict.get(position['Id'], None)
            if detected_obj is not None:
                for tag in detected_obj['detectedObject']['tags']:
                    if tag['name'] == 'gap':
                        color = (0, 0, 255)  # Red

            # Draw rectangle for planogram position
            img = cv2.rectangle(img, (x, y), (x+w, y+h), color, 6)

    for obj in detected_objects_dict.values():
        bb = obj['detectedObject']['boundingBox']
        x, y, w, h = bb['x'], bb['y'], bb['w'], bb['h']

        # Default detected object color is blue
        color = (255, 0, 0)  # Blue

        # Check for 'gap' tag
        for tag in obj['detectedObject']['tags']:
            if tag['name'] == 'gap':
                color = (0, 0, 255)  # Red

        # Draw rectangle for detected object
        _draw_dashed_rect(img, (x, y), (x+w, y+h), color, 6, 10)

    return img
