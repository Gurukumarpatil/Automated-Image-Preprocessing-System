import json
import boto3
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
        image_data = response["Body"].read()

        image = Image.open(BytesIO(image_data))
        image = image.convert("RGB")
        image.thumbnail((1024, 1024))

        output = BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)

        filename = key.split("/")[-1].rsplit(".", 1)[0] + ".jpg"
        output_key = "processed/" + filename

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=output.getvalue(),
            ContentType="image/jpeg"
        )

    return {
        "statusCode": 200,
        "body": json.dumps("Image processing completed")
    }