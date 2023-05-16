import argparse
from typing import Dict, Any

import cv2
import json
import numpy as np


def visualize_planogram(planogram: Dict[str, Any], target_width: int = 500) -> np.ndarray:
    # Calculate the scale factor and aspect ratio
    width = int(planogram['Width'])
    height = int(planogram['Height'])
    aspect_ratio = width / height
    scale = target_width / width
    target_height = target_width / aspect_ratio

    # Create a blank image with the scaled dimensions
    img = np.zeros((int(target_height), int(target_width), 3), dtype=np.uint8)

    # Loop over the positions and draw rectangles for each product
    for position in planogram['Positions']:
        product = next(p for p in planogram['Products'] if p['Id'] == position['ProductId'])
        x, y = int(position['X'] * scale), int(position['Y'] * scale)
        w, h = int(product['W'] * scale), int(product['H'] * scale)
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Loop over the fixtures and draw rectangles for each one
    for fixture in planogram['Fixtures']:
        x, y = int(fixture['X'] * scale), int(fixture['Y'] * scale)
        w, h = int(fixture['W'] * scale), int(fixture['H'] * scale)
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # Return the rendered image
    return img


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render the planogram based on a planogram JSON.')
    parser.add_argument('input_filename', type=str, help='Input planogram JSON filename.')
    parser.add_argument('output_filename', type=str, help='Output rendered image filename.')
    parser.add_argument('-w', '--width', type=int, default=500, help='Width of the rendered image. Default is 500.')

    args = parser.parse_args()

    # Load the planogram JSON
    with open(args.input_filename, 'r') as f:
        planogram = json.load(f)

    # Visualize the planogram
    img = visualize_planogram(planogram, args.width)

    # Save the rendered image
    cv2.imwrite(args.output_filename, img)
