import json
from typing import List
from urllib.parse import urlparse


class NormalizedCoordinate:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def to_dict(self) -> dict:
        return {
            'x': self.x,
            'y': self.y
        }


class ImageRectificationControlPoints:
    def __init__(self, top_left: NormalizedCoordinate, top_right: NormalizedCoordinate,
                 bottom_left: NormalizedCoordinate, bottom_right: NormalizedCoordinate) -> None:
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right

    def to_dict(self) -> dict:
        return {
            'topLeft': self.top_left.to_dict(),
            'topRight': self.top_right.to_dict(),
            'bottomLeft': self.bottom_left.to_dict(),
            'bottomRight': self.bottom_right.to_dict()
        }


class ImageRectificationRequest:
    def __init__(self, url: str, control_points: ImageRectificationControlPoints) -> None:
        if not self.is_valid_url(url):
            raise ValueError('The image URL must be a valid HTTP or HTTPS URL.')

        self.url = url
        self.control_points = control_points

    def is_valid_url(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            return all([parsed_url.scheme, parsed_url.netloc])
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {
            'url': self.url,
            'controlPoints': self.control_points.to_dict()
        }


class ImageStitchingRequest:
    def __init__(self, images: List[str]) -> None:
        if not (2 <= len(images) <= 20):
            raise ValueError('The number of images must be between 2 and 20.')
        if not all(self.is_valid_url(image_url) for image_url in images):
            raise ValueError('All image URLs must be valid.')

        self.images = images

    def is_valid_url(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            return all([parsed_url.scheme, parsed_url.netloc])
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {'images': self.images}
