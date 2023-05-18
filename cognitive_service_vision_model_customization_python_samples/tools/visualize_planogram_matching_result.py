from typing import Dict, Any

import cv2
import numpy as np


def visualize_matching_result(img: np.ndarray, matching_result: Dict[str, Any], planogram: Dict[str, Any]) -> np.ndarray:
    # Image dimensions
    img_height, img_width = img.shape[:2]

    # Create a dictionary of detected objects by positionId for easy lookup
    matching_result_dict = {obj['positionId']: obj for obj in matching_result['matchingResultPerPosition']}

    # Create a dictionary of planogram positions by Id for easy lookup
    positions_dict = {position['Id']: position for position in planogram['Positions']}
    
    # Create a dictionary of products by Id for easy lookup
    products_dict = {product['Id']: product for product in planogram['Products']}

    for positionId, detected_obj in matching_result_dict.items():
        # If the detected object's position is not in the planogram, skip it
        if positionId not in positions_dict:
            continue

        # Normalize boundingBox coordinates and convert to pixel coordinates
        bb = detected_obj['detectedObject']['boundingBox']
        x = int((bb['x'] / img_width) * img_width)
        y = int((bb['y'] / img_height) * img_height)
        w = int((bb['w'] / img_width) * img_width)
        h = int((bb['h'] / img_height) * img_height)

        # Get the position and product for this detected object
        position = positions_dict[positionId]
        product = products_dict.get(position['ProductId'], None)
        if product is None:
            raise Exception(f"Planogram corrupted: Product with Id {position['ProductId']} not found in planogram.")

        # If the detected object's tag matches the product's name, change box color to green and label to 'Matched Product'
        tag = detected_obj['detectedObject']['tags'][0]
        if tag['name'] == product['Name'] or tag['name'] == 'product':
            color = (0, 255, 0)  # Green
            label = 'Matched Product'
        elif tag['name'] == 'gap':
            color = (0, 0, 255)  # Red
            label = 'Missing Product'
            print(f'Missing Product in position {positionId}, expected {product["Name"]} but found gap')
        else:
            color = (255, 0, 255) # Magenta
            label = 'Misplaced Product'
            print(f'Misplaced Product in position {positionId}, expected {product["Name"]} but found {tag["name"]}')

        # Draw rectangle for detected object and put text annotation
        img = cv2.rectangle(img, (x, y), (x+w, y+h), color, 6, 10)
        cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    return img
