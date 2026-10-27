import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO
from urllib.parse import unquote_plus

import boto3
from PIL import Image, ImageFilter, ImageStat


TABLE_NAME = os.environ["TABLE_NAME"]
MAX_IMAGE_BYTES = int(os.environ.get("MAX_IMAGE_BYTES", "10485760"))


def _decimal(value):
    return Decimal(str(round(value, 2)))


def analyze_image(image_bytes):
    """Return deterministic image-quality metrics without an external AI service."""
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError(f"Image exceeds the {MAX_IMAGE_BYTES}-byte limit")

    with Image.open(BytesIO(image_bytes)) as source:
        source.verify()

    with Image.open(BytesIO(image_bytes)) as source:
        image_format = source.format or "UNKNOWN"
        original_width, original_height = source.size
        rgb = source.convert("RGB")
        rgb.thumbnail((1024, 1024))
        gray = rgb.convert("L")

        stats = ImageStat.Stat(gray)
        brightness = stats.mean[0]
        contrast = stats.stddev[0]
        edge_mean = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0]
        sharpness = min(100.0, edge_mean * 4.0)
        average_color = [_decimal(channel) for channel in ImageStat.Stat(rgb).mean]

    dimension_score = min(100.0, (original_width * original_height) / 921600 * 100)
    brightness_score = max(0.0, 100.0 - abs(brightness - 128.0) * 1.4)
    contrast_score = min(100.0, contrast * 2.5)
    quality_score = (
        dimension_score * 0.25
        + brightness_score * 0.2
        + contrast_score * 0.25
        + sharpness * 0.3
    )

    if quality_score >= 70:
        quality = "good"
    elif quality_score >= 45:
        quality = "acceptable"
    else:
        quality = "needs_review"

    return {
        "format": image_format,
        "width": original_width,
        "height": original_height,
        "brightness": _decimal(brightness),
        "contrast": _decimal(contrast),
        "sharpness": _decimal(sharpness),
        "quality_score": _decimal(quality_score),
        "quality": quality,
        "average_color_rgb": average_color,
    }


def handler(event, context):
    s3 = boto3.client("s3")
    table = boto3.resource("dynamodb").Table(TABLE_NAME)
    processed = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        print(f"Analysiere Bildqualität: {key} aus Bucket: {bucket}")

        response = s3.get_object(Bucket=bucket, Key=key)
        metrics = analyze_image(response["Body"].read())
        metrics.update(
            {
                "image_id": key,
                "bucket": bucket,
                "object_size_bytes": response.get("ContentLength", 0),
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        table.put_item(Item=metrics)
        processed.append(key)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Bilder erfolgreich analysiert und gespeichert.",
                "processed": processed,
            }
        ),
    }
