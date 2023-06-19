import os
import boto3
import tqdm
from modules.helpers.constant import CloudStorage


class StorageS3:
    def __init__(self):
        self._s3_resource = boto3.resource(**CloudStorage.S3_CONFIG)
        self._s3_client = boto3.client(**CloudStorage.S3_CONFIG)
        self._bucket = self._s3_resource.Bucket(CloudStorage.BUCKET)

    def s3_upload_file(self, file_byte, file_storage_path):
        self._s3_client.upload_fileobj(
            file_byte, CloudStorage.BUCKET, file_storage_path
        )

    def s3_download_file(self, file_local_path, file_storage_path):
        self._s3_resource.Bucket(CloudStorage.BUCKET).download_file(
            Key=file_storage_path, Filename=file_local_path
        )

    def s3_delete_object(self, file_storage_path):
        self._bucket.objects.filter(Prefix=file_storage_path).delete()

    def s3_upload_directory(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                self._s3_client.upload_file(
                    os.path.join(root, file),
                    CloudStorage.BUCKET,
                    file,
                    os.path.join(root, file),
                )

    def s3_upload_large_file(self, session, *, key, filename):
        """
        Upload a file to S3 with a progress bar.
        """
        file_size = os.stat(filename).st_size

        s3 = session.client("s3")

        with tqdm.tqdm(
            total=file_size, unit="B", unit_scale=True, desc=filename
        ) as pbar:
            self._s3_client.upload_file(
                Filename=filename,
                Bucket=CloudStorage.BUCKET,
                Key=key,
                Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
            )


storage_s3 = StorageS3()
