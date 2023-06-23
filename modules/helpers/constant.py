import os


class DagConstant:
    GENERATE_PROMPTS_PATH = "resources/generate_prompts.csv"
    RETRIEVAL_PATH = "resources/retrieval_df.csv"
    BASE_SRC_PATH = "resources/dataset/source/{0}.png"
    BASE_DST_PATH = "resources/dataset/target/{0}.png"
    PROMPT_FILE_PATH = "resources/dataset/prompt.json"


class CloudStorage:
    S3_CONFIG = {
        "service_name": "s3",
        "region_name": "ap-southeast-1",
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    }
    BUCKET = "stable-diffusion-dataset"
