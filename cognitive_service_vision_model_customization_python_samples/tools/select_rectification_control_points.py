import argparse
import json

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple


class CornerSelector:
    def __init__(self):
        self._image = None
        self._points = []

    def interactive_select(self, image: np.ndarray) -> np.ndarray:
        self._image = image
        window_name = 'Please select four corners in clockwise order'
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self._click_callback)

        while True:
            cv2.imshow(window_name, self._image)
            cv2.waitKey(20)
            if len(self._points) == 4:
                cv2.destroyAllWindows()
                return np.array(self._points)

    def _click_callback(self, event: int, x: int, y: int, flags: int, param: Any) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self._image, (x, y), 5, (0, 0, 255), 2)
            self._points.append((x, y))


def image_resize(image: np.ndarray, shorter_edge: int) -> Tuple[np.ndarray, Tuple[int, int]]:
    dim = None
    (h, w) = image.shape[:2]

    if w < h:
        r = shorter_edge / float(w)
        width = shorter_edge
        height = int(h * r)
    else:
        r = shorter_edge / float(h)
        width = int(w * r)
        height = shorter_edge

    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized, dim


def select_four_corners(image: np.ndarray) -> List[List[float]]:
    img, dim = image_resize(image, shorter_edge=1024)
    corners = CornerSelector().interactive_select(img)
    corners_relative = []
    for corner in corners:
        tmp_x = corner[0] / dim[0]
        tmp_y = corner[1] / dim[1]
        corners_relative.append([tmp_x, tmp_y])

    return corners_relative


def convert_to_control_points_format(corner_points: List[List[float]]) -> Dict[str, Dict[str, Dict[str, float]]]:
    control_points = {
        "topLeft": {
            "x": corner_points[0][0],
            "y": corner_points[0][1]
        },
        "topRight": {
            "x": corner_points[1][0],
            "y": corner_points[1][1]
        },
        "bottomRight": {
            "x": corner_points[2][0],
            "y": corner_points[2][1]
        },
        "bottomLeft": {
            "x": corner_points[3][0],
            "y": corner_points[3][1]
        }
    }

    return {'ControlPoints': control_points}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select corners of an image interactively.')
    parser.add_argument('input_filename', type=str, help='Input image file')

    args = parser.parse_args()

    image = cv2.imread(args.input_filename)
    # Select four corners interactively and convert corner points to control points format
    payload = convert_to_control_points_format(select_four_corners(image))
    print(json.dumps(payload, indent=4))
