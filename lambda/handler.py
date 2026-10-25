import json
import os
from urllib.parse import unquote_plus

import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    processed = []

    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])

        print(f"Verarbeite Bild: {key} aus Bucket: {bucket}")
        image = {'S3Object': {'Bucket': bucket, 'Name': key}}

        response_labels = rekognition.detect_labels(
            Image=image,
            MaxLabels=10,
            MinConfidence=75
        )
        labels = [label['Name'] for label in response_labels.get('Labels', [])]

        response_text = rekognition.detect_text(Image=image)
        detected_texts = [
            text['DetectedText']
            for text in response_text.get('TextDetections', [])
            if text.get('Type') == 'LINE'
        ]

        table.put_item(
            Item={
                'image_id': key,
                'bucket': bucket,
                'labels': labels,
                'detected_text': detected_texts
            }
        )
        processed.append(key)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Bilder erfolgreich analysiert und gespeichert.',
            'processed': processed
        })
    }