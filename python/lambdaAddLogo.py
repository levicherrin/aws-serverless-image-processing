import boto3
from PIL import Image, ImageOps
from io import BytesIO
import urllib.parse
import json
import os

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    body = json.loads(event['Records'][0]['body'])
    bucket = body['Records'][0]['s3']['bucket']['name']
    key = body['Records'][0]['s3']['object']['key']    
    
    print("BUCKET: " + bucket, "KEY: " + key)
    newKey = key[7:]
    print("BUCKET: " + bucket, "NEWKEY: " + newKey)
    
    try:
        boto3.resource('s3').meta.client.download_file(bucket, "logo/Kevinlogo1.png", '/tmp/Kevinlogo1.png')
        file = os.path.isfile('/tmp/Kevinlogo1.png')
        if file: False

        print("Logo downloaded: " +str(file))
        
        in_mem_file = BytesIO()

        file_byte_string = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
        im = Image.open(BytesIO(file_byte_string))
        imLogo = Image.open('/tmp/Kevinlogo1.png')

        width, height = im.size
        widthLogo = int(width/5)
        heightLogo = int(height/5)

        imLogo = ImageOps.contain(imLogo, (widthLogo, heightLogo))
        widthLogo, heightLogo = imLogo.size
        
        im.paste(imLogo, (width - widthLogo, height - heightLogo), imLogo)

        im.save(in_mem_file, format='jpeg')
        in_mem_file.seek(0)

        response = s3.put_object(
            Body=in_mem_file,
            Bucket= "image-processing-kevin",
            Key= "fulls/" + newKey,
            ContentType='image/jpeg'
        )

        im.close()
        imLogo.close()

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e