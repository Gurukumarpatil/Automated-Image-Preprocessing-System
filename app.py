
import os
import uuid
from io import BytesIO

import boto3

from flask import (
    Flask, render_template, request,
    send_file, redirect, url_for, flash, abort
)
from werkzeug.utils import secure_filename
from config import Config
from PIL import Image, UnidentifiedImageError
from database.db import get_db_connection
from botocore.exceptions import ClientError


app = Flask(__name__)
app.config.from_object(Config)

# AWS S3 connection
s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


@app.route("/")
def home():
     return redirect(url_for("dashboard"))

@app.route("/upload", methods=["GET"])
def upload_page():
    return render_template("index.html")


# ---------------------------------
# IMAGE UPLOAD
# ---------------------------------

@app.route("/upload", methods=["POST"])
def upload():

    if "image" not in request.files:
        return "No image selected", 400

    file = request.files["image"]

    if file.filename == "":
        return "No file selected", 400

    if "." not in file.filename:
        return "Invalid filename.", 400

    extension = file.filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return "Only JPG, JPEG, PNG and WEBP are allowed.", 400

    # Validate image content
    try:
        image = Image.open(file.stream)
        image.verify()
        file.stream.seek(0)

    except (UnidentifiedImageError, OSError, ValueError):
        return "Invalid or corrupted image file.", 400

    filename = secure_filename(file.filename)

    # Calculate original image size in bytes
    file.stream.seek(0, 2)
    original_size = file.stream.tell()
    file.stream.seek(0)

    s3_key = f"original/{uuid.uuid4().hex}_{filename}"

    try:
        # Upload original image to S3
        s3.upload_fileobj(
            file.stream,
            BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.mimetype}
        )

        # Save metadata in RDS
        connection = get_db_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO images
                    (original_filename, original_s3_key, status, original_size)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (filename, s3_key, "PROCESSING", original_size)
                )

            connection.commit()

        finally:
            connection.close()

        return redirect(url_for("dashboard"))

    except Exception:
        app.logger.exception("Image upload or database operation failed")
        return "Upload failed. Check server logs.", 500


# ---------------------------------
# DASHBOARD WITH COMPRESSION STATS
# ---------------------------------

@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT * FROM images
                ORDER BY uploaded_at DESC
            """)

            images = cursor.fetchall()

            for image in images:

                original_key = image["original_s3_key"]

                # Generate original image URL
                image["original_url"] = s3.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": BUCKET_NAME,
                        "Key": original_key
                    },
                    ExpiresIn=3600
                )

                # Derive processed image key
                filename = original_key.split("/")[-1].rsplit(".", 1)[0]
                processed_key = f"processed/{filename}.jpg"

                try:
                    # Check whether Lambda created the processed image
                    response = s3.head_object(
                        Bucket=BUCKET_NAME,
                        Key=processed_key
                    )

                    # Get processed image size
                    processed_size = response["ContentLength"]

                    original_size = image["original_size"]

                    # Calculate compression percentage
                    if original_size and original_size > 0:

                        compression_percentage = (
                            (original_size - processed_size)
                            / original_size
                        ) * 100

                        compression_percentage = round(
                            compression_percentage, 2
                        )

                    else:
                        compression_percentage = None

                    # Update image information
                    image["processed_s3_key"] = processed_key
                    image["processed_size"] = processed_size
                    image["compression_percentage"] = compression_percentage
                    image["status"] = "COMPLETED"

                    # Generate processed image URL
                    image["processed_url"] = s3.generate_presigned_url(
                        "get_object",
                        Params={
                            "Bucket": BUCKET_NAME,
                            "Key": processed_key
                        },
                        ExpiresIn=3600
                    )

                    # Save processing information in RDS
                    cursor.execute("""
                        UPDATE images
                        SET processed_s3_key = %s,
                            processed_size = %s,
                            compression_percentage = %s,
                            status = %s
                        WHERE id = %s
                    """, (
                        processed_key,
                        processed_size,
                        compression_percentage,
                        "COMPLETED",
                        image["id"]
                    ))

                except ClientError as error:

                    error_code = error.response.get(
                        "Error", {}
                    ).get("Code")

                    if error_code in ("404", "NoSuchKey", "NotFound"):

                        image["processed_url"] = None
                        image["status"] = "PROCESSING"

                    else:
                        raise

            connection.commit()

    finally:
        connection.close()

    return render_template("dashboard.html", images=images)


# ---------------------------------
# DOWNLOAD ORIGINAL IMAGE
# ---------------------------------

@app.route("/download/<int:image_id>/original")
def download_original(image_id):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM images WHERE id = %s",
                (image_id,)
            )
            image = cursor.fetchone()

    finally:
        connection.close()

    if not image:
        abort(404)

    file_data = BytesIO()

    s3.download_fileobj(
        BUCKET_NAME,
        image["original_s3_key"],
        file_data
    )

    file_data.seek(0)

    return send_file(
        file_data,
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name=image["original_filename"]
    )


# ---------------------------------
# DOWNLOAD PROCESSED IMAGE
# ---------------------------------

@app.route("/download/<int:image_id>/processed")
def download_processed(image_id):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM images WHERE id = %s",
                (image_id,)
            )
            image = cursor.fetchone()

    finally:
        connection.close()

    if not image:
        abort(404)

    processed_key = image["processed_s3_key"]

    if not processed_key:
        filename = image["original_s3_key"].split("/")[-1].rsplit(".", 1)[0]
        processed_key = f"processed/{filename}.jpg"

    file_data = BytesIO()

    try:
        s3.download_fileobj(
            BUCKET_NAME,
            processed_key,
            file_data
        )

    except ClientError as error:

        error_code = error.response.get("Error", {}).get("Code")

        if error_code in ("404", "NoSuchKey", "NotFound"):
            return "Processed image is not available yet.", 404

        raise

    file_data.seek(0)

    return send_file(
        file_data,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name=os.path.basename(processed_key)
    )


# ---------------------------------
# DELETE IMAGE
# ---------------------------------

@app.route("/delete/<int:image_id>", methods=["POST"])
def delete_image(image_id):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT * FROM images WHERE id = %s",
                (image_id,)
            )

            image = cursor.fetchone()

            if not image:
                abort(404)

            original_key = image["original_s3_key"]

            processed_key = image["processed_s3_key"]

            if not processed_key:
                filename = original_key.split("/")[-1].rsplit(".", 1)[0]
                processed_key = f"processed/{filename}.jpg"

            # Delete original image from S3
            s3.delete_object(
                Bucket=BUCKET_NAME,
                Key=original_key
            )

            # Delete processed image from S3
            s3.delete_object(
                Bucket=BUCKET_NAME,
                Key=processed_key
            )

            # Delete database record
            cursor.execute(
                "DELETE FROM images WHERE id = %s",
                (image_id,)
            )

        connection.commit()

        flash(
            "Image and its database record deleted successfully.",
            "success"
        )

    except Exception:
        connection.rollback()
        app.logger.exception("Image deletion failed")
        return "Image deletion failed. Check server logs.", 500

    finally:
        connection.close()

    return redirect(url_for("dashboard"))


# ---------------------------------
# RUN APPLICATION
# ---------------------------------

if __name__ == "__main__":
    app.run(debug=True)
