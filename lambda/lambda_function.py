
import json
import boto3
import os
from PIL import Image, ImageOps
from io import BytesIO
from urllib.parse import unquote_plus

s3 = boto3.client("s3")

MAX_DIMENSIONS = (1920, 1920)
JPEG_QUALITIES = [85, 75, 65, 55]


def lambda_handler(event, context):

    for record in event["Records"]:

        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        if not key.startswith("original/"):
            continue

        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        original_data = response["Body"].read()
        original_size = len(original_data)

        # Open image and correct EXIF orientation
        image = Image.open(BytesIO(original_data))
        image = ImageOps.exif_transpose(image)

        # Detect transparency before changing image mode
        has_transparency = (
            "A" in image.getbands()
            or "transparency" in image.info
        )

        # Resize while maintaining aspect ratio
        image.thumbnail(
            MAX_DIMENSIONS,
            Image.Resampling.LANCZOS
        )

        output_data = original_data
        output_extension = os.path.splitext(key)[1].lower()

        # ---------------------------------
        # TRANSPARENT IMAGE: OPTIMIZED PNG
        # ---------------------------------

        if has_transparency:

            png_image = image.convert("RGBA")

            output = BytesIO()

            png_image.save(
                output,
                format="PNG",
                optimize=True,
                compress_level=9
            )

            candidate = output.getvalue()

            if len(candidate) < original_size:

                output_data = candidate
                output_extension = ".png"

        # ---------------------------------
        # OPAQUE IMAGE: JPEG COMPRESSION
        # ---------------------------------

        else:

            rgb_image = image.convert("RGB")

            for quality in JPEG_QUALITIES:

                output = BytesIO()

                rgb_image.save(
                    output,
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                    progressive=True
                )

                candidate = output.getvalue()

                if len(candidate) < original_size:

                    output_data = candidate
                    output_extension = ".jpg"
                    break

        # ---------------------------------
        # SAVE PROCESSED IMAGE
        # ---------------------------------

        filename = os.path.splitext(
            os.path.basename(key)
        )[0]

        output_key = (
            "processed/"
            + filename
            + output_extension
        )

        if output_extension == ".jpg" and output_data != original_data:
            content_type = "image/jpeg"

        elif output_extension == ".png" and output_data != original_data:
            content_type = "image/png"

        else:
            content_type = (
                response.get("ContentType")
                or "application/octet-stream"
            )

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=output_data,
            ContentType=content_type
        )

        processed_size = len(output_data)
        saved_bytes = original_size - processed_size

        savings_percentage = round(
            (saved_bytes / original_size) * 100,
            2
        ) if original_size else 0

        print("Original key:", key)
        print("Processed key:", output_key)
        print("Original size:", original_size)
        print("Processed size:", processed_size)
        print("Bytes saved:", saved_bytes)
        print("Savings percentage:", savings_percentage)

    return {
        "statusCode": 200,
        "body": json.dumps("Image processing completed")
    }
