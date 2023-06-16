import io
import os
from PIL import Image
import numpy as np


def load(img: bytes) -> Image:
    """Load the bytestring as an image"""
    bytes_ = io.BytesIO(img)
    return Image.open(bytes_).convert("RGB")


def bytes_to_array(b: bytes) -> np.ndarray:
    return Image.fromarray(
        np.frombuffer(b, dtype=np.uint8).reshape((512, 512, 3))
    ).convert("RGB")


def make_resource_dir():
    os.makedirs("resources/dataset", exist_ok=True)
    os.makedirs("resources/dataset/source", exist_ok=True)
    os.makedirs("resources/dataset/target", exist_ok=True)
