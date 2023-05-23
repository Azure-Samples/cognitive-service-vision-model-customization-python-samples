import argparse
import json
from typing import Dict, Any

import cv2
import numpy as np


def visualize_recognition_result(result: Dict[str, Any], img: np.ndarray, threshold: float = 0.3) -> np.ndarray:
    # Loop over the products and draw rectangles for each one
    for product in result['products']:
        if product['tags'][0]['confidence'] > threshold:
            l, t, w, h = product['boundingBox']['x'], product['boundingBox']['y'], product['boundingBox']['w'], product['boundingBox']['h']
            img = cv2.rectangle(img, (l, t), (l + w, t + h), (0, 255, 0), 5)
            # For better visualization, only show the first 15 characters of the label
            img = cv2.putText(img, product['tags'][0]['name'][0:15], (l, t - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Loop over the gaps and draw rectangles for each one
    for product in result['gaps']:
        if product['tags'][0]['confidence'] > threshold:
            l, t, w, h = product['boundingBox']['x'], product['boundingBox']['y'], product['boundingBox']['w'], product['boundingBox']['h']
            img = cv2.rectangle(img, (l, t), (l + w, t + h), (255, 0, 0), 5)
            img = cv2.putText(img, 'gap', (l, t - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Return the visualized image
    return img


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize prediction results from JSON file and image file.')
    parser.add_argument('result_filename', type=str, help='JSON file containing the prediction results.')
    parser.add_argument('image_filename', type=str, help='Image file used for predictions.')
    parser.add_argument('output_filename', type=str, help='Output rendered image filename.')
    parser.add_argument('-t', '--threshold', type=int, default=0.3, help='Confidence threshold to filter out low confidence prediction, default is 0.3.')

    args = parser.parse_args()

    # Load the prediction result
    with open(args.result_filename, 'r') as f:
        result = json.load(f)

    # Read the source image
    img = cv2.imread(args.image_filename)

    # Visualize and save the result
    img = visualize_recognition_result(result, img, args.threshold)
    cv2.imwrite(args.output_filename, img)
