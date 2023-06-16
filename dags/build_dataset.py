"""DAG for ETL room dataset"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timedelta
from math import ceil

import dask.dataframe as dd
import numpy as np
from airflow.decorators import dag, task
from PIL import Image

sys.path.append(os.getcwd())

from modules.components.caption_images import CaptionImagesComponent
from modules.components.download_images import DownloadImagesComponent
from modules.components.generate_prompts import GeneratePromptsComponent
from modules.components.prompt_based_laion_retrieval import LAIONRetrievalComponent
from modules.components.segment_images import SegmentImagesComponent
from modules.helpers.constant import DagConstant
from modules.helpers.utils import bytes_to_array, load, make_resource_dir

default_args = {"owner": "minhhnh", "retries": 5, "retry_delay": timedelta(minutes=2)}


@dag(
    dag_id="build_dataset",
    default_args=default_args,
    start_date=datetime(2023, 6, 15),
    schedule_interval="@daily",
    catchup=False,
)
def build_dataset():
    """DAG for get full data and save to nested dict."""

    @task(multiple_outputs=False)
    def generate_prompts():
        df_generate_prompts = GeneratePromptsComponent.load()
        df_generate_prompts.compute().to_csv(DagConstant.GENERATE_PROMPTS_PATH)
        return DagConstant.GENERATE_PROMPTS_PATH

    @task(multiple_outputs=False)
    def data_retrieval(generate_prompts_path: str):
        df_generate_prompts = dd.read_csv(generate_prompts_path)
        laion_retrieval_component = LAIONRetrievalComponent()

        retrieval_df = laion_retrieval_component.transform(
            df_generate_prompts, num_images=10
        )
        retrieval_df.compute().to_csv(DagConstant.RETRIEVAL_PATH)
        return DagConstant.RETRIEVAL_PATH

    @task(multiple_outputs=False)
    def transform(retrieval_path: str):
        df_retrieval = dd.read_csv(retrieval_path)
        npart = ceil(len(df_retrieval) / 100)
        parted_df = df_retrieval.repartition(npartitions=npart)

        download_component = DownloadImagesComponent()
        caption_image_component = CaptionImagesComponent()
        segment_component = SegmentImagesComponent()

        make_resource_dir()
        prompt_file = open(DagConstant.PROMPT_FILE_PATH, "a+")

        skip_part = 0

        for sub_retrieval_df in parted_df.partitions:
            if skip_part > 0:
                skip_part -= 1
                continue
            print(sub_retrieval_df.compute())

            downloaded_df = download_component.transform(sub_retrieval_df)
            downloaded_df = downloaded_df.dropna()

            try:
                downloaded_df.compute().to_csv(
                    "resources/downloaded_df.csv", index=False
                )
            except Exception as e:
                print(e)
                continue

            downloaded_df["captions_text"] = caption_image_component.transform(
                downloaded_df
            )["captions_text"]

            downloaded_df["segmentations_data"] = segment_component.transform(
                downloaded_df
            )["segmentations_data"]

            for _, row in downloaded_df.iterrows():
                dst_img = load(row["images_data"])
                src_img = bytes_to_array(row["segmentations_data"])

                img_id = row["id"]
                caption = row["captions_text"]
                dst_img.save(DagConstant.BASE_DST_PATH.format(img_id))
                src_img.save(DagConstant.BASE_SRC_PATH.format(img_id))
                promt = {
                    "source": DagConstant.BASE_SRC_PATH[18:].format(img_id),
                    "target": DagConstant.BASE_DST_PATH[18:].format(img_id),
                    "prompt": caption,
                }

                prompt_file.write(json.dumps(promt) + "\n")
                prompt_file.flush()

    @task(multiple_outputs=False)
    def upload_file_to_s3(generate_prompts_path: str):
        pass

    transform(data_retrieval(generate_prompts()))


dag = build_dataset()
