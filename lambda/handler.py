from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, TypedDict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

rekognition_client = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")


class LabelResult(TypedDict):
    name: str
    confidence: Decimal


def _json_serializer(value: Any) -> str | float:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "body": json.dumps(payload, default=_json_serializer),
    }


def _extract_labels(bucket: str, key: str) -> list[LabelResult]:
    response = rekognition_client.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=10,
        MinConfidence=70,
    )

    labels: list[LabelResult] = []
    for entry in response.get("Labels", []):
        name = entry.get("Name")
        confidence = entry.get("Confidence")
        if not isinstance(name, str) or confidence is None:
            continue

        labels.append(
            {
                "name": name,
                "confidence": Decimal(str(confidence)),
            }
        )

    return labels


def _store_metadata(table_name: str, bucket: str, key: str, labels: list[LabelResult]) -> dict[str, Any]:
    image_id = str(uuid.uuid4())
    processed_at = datetime.now(timezone.utc)

    item = {
        "image_id": image_id,
        "bucket": bucket,
        "object_key": key,
        "label_count": len(labels),
        "labels": labels,
        "processed_at": processed_at.isoformat(),
    }

    table = dynamodb.Table(table_name)
    table.put_item(Item=item)

    return item


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context

    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        logger.error("Missing TABLE_NAME environment variable")
        return _response(500, {"message": "Server misconfiguration: TABLE_NAME is missing"})

    records = event.get("Records")
    if not isinstance(records, list) or not records:
        logger.warning("Invalid or empty S3 event payload")
        return _response(400, {"message": "Invalid S3 event payload"})

    processed_items: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for index, record in enumerate(records):
        try:
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]

            if not isinstance(bucket, str) or not isinstance(key, str):
                raise TypeError("S3 bucket or object key is invalid")

            labels = _extract_labels(bucket=bucket, key=key)
            metadata = _store_metadata(table_name=table_name, bucket=bucket, key=key, labels=labels)
            processed_items.append(metadata)
        except (KeyError, TypeError, ValueError, BotoCoreError, ClientError) as exc:
            logger.exception("Failed processing S3 event record at index %s", index)
            errors.append({"record_index": index, "error": str(exc)})

    if errors and not processed_items:
        return _response(500, {"message": "Processing failed", "errors": errors})

    if errors:
        return _response(
            207,
            {
                "message": "Partial success",
                "processed_items": processed_items,
                "errors": errors,
            },
        )

    return _response(200, {"message": "Processing completed", "processed_items": processed_items})
