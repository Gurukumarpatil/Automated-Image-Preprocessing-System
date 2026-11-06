
import json
import boto3
import os
import mimetypes
from PIL import Image
from io import BytesIO
from urllib.parse import unquote_plus

s3 = boto3.client("s3")


def lambda_handler(event, context):

    for record in event["Records"]:

        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        if not key.startswith("original/"):
            continue

        response = s3.get_object(Bucket=bucket, Key=key)
        original_data = response["Body"].read()

        image = Image.open(BytesIO(original_data))
        original_format = image.format or "JPEG"

        # Resize large images while preserving aspect ratio
        image.thumbnail((1024, 1024))

        # Try JPEG compression
        rgb_image = image.convert("RGB")

        jpeg_output = BytesIO()
        rgb_image.save(
            jpeg_output,
            format="JPEG",
            quality=85,
            optimize=True
        )

        jpeg_data = jpeg_output.getvalue()

        # Use JPEG only when it actually reduces file size
        if len(jpeg_data) < len(original_data):

            output_data = jpeg_data
            extension = ".jpg"
            content_type = "image/jpeg"

        else:

            # Keep original bytes and format if JPEG is larger
            output_data = original_data
            extension = os.path.splitext(key)[1].lower()

            content_type = (
                mimetypes.guess_type("image" + extension)[0]
                or "application/octet-stream"
            )

        filename = os.path.splitext(os.path.basename(key))[0]
        output_key = "processed/" + filename + extension

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=output_data,
            ContentType=content_type
        )

        print("Original size:", len(original_data))
        print("Processed size:", len(output_data))
        print("Storage saved:", len(original_data) - len(output_data))

    return {
        "statusCode": 200,
        "body": json.dumps("Image processing completed")
    }
