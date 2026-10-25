import json
import os
import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    try:
        # S3 Event auslesen
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        print(f"Verarbeite Bild: {key} aus Bucket: {bucket}")
        
        # 1. Objekterkennung (Labels)
        response_labels = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10,
            MinConfidence=75
        )
        labels = [label['Name'] for label in response_labels['Labels']]
        
        # 2. Texterkennung (Text)
        response_text = rekognition.detect_text(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        detected_texts = [text['DetectedText'] for text in response_text.get('TextDetections', [])]
        
        # In DynamoDB speichern
        table.put_item(
            Item={
                'image_id': key,
                'bucket': bucket,
                'labels': labels,
                'detected_text': detected_texts
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Bild erfolgreich analysiert und in DynamoDB gespeichert!')
        }
        
    except Exception as e:
        print(f"Fehler bei der Bildverarbeitung: {str(e)}")
        raise e