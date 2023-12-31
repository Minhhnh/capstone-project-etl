"""
This component that captions images using a model from the Hugging Face hub.
"""
import io
import logging
import typing as t

import dask.dataframe as dd
import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import BatchEncoding, BlipProcessor, BlipForConditionalGeneration


def process_image(
    image: bytes, *, processor: BlipProcessor, device: str
) -> torch.Tensor:
    """
    Process the image to a tensor.

    Args:
        image: The input image as a byte string.
        processor: The processor object for transforming the image.
        device: The device to move the transformed image to.
    """

    def load(img: bytes) -> Image:
        """Load the bytestring as an image"""
        bytes_ = io.BytesIO(img)
        return Image.open(bytes_).convert("RGB")

    def transform(img: Image) -> BatchEncoding:
        """
        Transform the image to a tensor using a processor and move it to the specified device.
        """
        return processor(images=img, return_tensors="pt").to(device)

    return transform(load(image))["pixel_values"]


def caption_image_batch(
    image_batch: pd.DataFrame,
    *,
    model: BlipForConditionalGeneration,
    processor: BlipProcessor,
    max_new_tokens: int,
) -> pd.Series:
    """Caption a batch of images"""
    input_batch = torch.cat(image_batch.tolist())
    output_batch = model.generate(
        pixel_values=input_batch, max_new_tokens=max_new_tokens
    )
    captions_batch = processor.batch_decode(
        output_batch, skip_special_tokens=True)

    return pd.Series(captions_batch, index=image_batch.index)


def caption_images(
    images: pd.Series,
    *,
    model: BlipForConditionalGeneration,
    processor: BlipProcessor,
    batch_size: int,
    max_new_tokens: int,
    device: str,
) -> pd.DataFrame:
    """Caption a pandas series of images"""
    images = images.apply(process_image, processor=processor, device=device)
    results: t.List[pd.Series] = []
    for batch in np.split(images, np.arange(batch_size, len(images), batch_size)):
        if not batch.empty:
            results.append(
                caption_image_batch(
                    batch,
                    model=model,
                    processor=processor,
                    max_new_tokens=max_new_tokens,
                ).T
            )
    return pd.concat(results).to_frame()


class CaptionImagesComponent:
    """
    Component that captions images using a model from the Hugging Face hub.
    """

    def __init__(self, model_id: str = "Salesforce/blip-image-captioning-base",) -> None:
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Device caption image component: {device}")

        self.device = device
        self.processor = BlipProcessor.from_pretrained(model_id)
        self.model = BlipForConditionalGeneration.from_pretrained(
            model_id).to(device)

    def transform(
        self,
        dataframe: dd.DataFrame,
        batch_size: int = 32,
        max_new_tokens: int = 50,
    ) -> dd.DataFrame:
        """
        Args:
            dataframe: Dask dataframe
            model_id: id of the model on the Hugging Face hub
            batch_size: batch size to use
            max_new_tokens: maximum token length of each caption

        Returns:
            Dask dataframe
        """

        dataframe = dataframe["images_data"].map_partitions(
            caption_images,
            model=self.model,
            processor=self.processor,
            batch_size=batch_size,
            max_new_tokens=max_new_tokens,
            device=self.device,
            meta={0: str},
        )
        dataframe.columns = ["captions_text"]

        return dataframe
