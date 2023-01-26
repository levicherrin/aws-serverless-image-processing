import boto3
from PIL import Image, ImageOps
from io import BytesIO
import urllib.parse
import json

print('Loading function')

client = boto3.client('s3')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # # Get the object from the event and show its content type
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    body = json.loads(event['Records'][0]['body'])
    bucket = body['Records'][0]['s3']['bucket']['name']
    key = body['Records'][0]['s3']['object']['key']    
    
    print("BUCKET: " + bucket, "KEY: " + key)
    try:
        in_mem_file = BytesIO()

        file_byte_string = client.get_object(Bucket=bucket, Key=key)['Body'].read()
        im = Image.open(BytesIO(file_byte_string))

        width, height = im.size
        ImageOps.contain(im, (width, height))
        
        im.save(in_mem_file, format='jpeg')
        in_mem_file.seek(0)

        # count = 0
        # bucket1 = s3.Bucket('image-processing-kevin')
        # for obj in bucket1.objects.filter(Prefix='copies/'):
        #     print('count start: '+str(count))
        #     count += 1
        #     print('Coutn end: '+str(count))

        response = client.put_object(
            Body=in_mem_file,
            Bucket= "image-processing-kevin",
            Key= "copies/{}".format(key),
            ContentType='image/jpeg'
        )

        im.close()

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e