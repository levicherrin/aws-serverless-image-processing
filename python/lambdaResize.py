import boto3
from PIL import Image, ImageOps
from io import BytesIO
import urllib.parse
import json

s3 = boto3.resource('s3')

# @profile
def resize_image(src_bucket, photo, boundbox, des_bucket):
        
    client = boto3.client('s3')
    in_mem_file = BytesIO()

    try:
        file_byte_string = client.get_object(Bucket=src_bucket.name, Key=photo)['Body'].read()
        im = Image.open(BytesIO(file_byte_string))

        #start of my code
        width, height = im.size   # Get dimensions
        aspectRatio = width / height
        thumbHeight = 491
        thumbWidth = 635
        thumbRatio = thumbWidth / thumbHeight

        #cut pixels off the sides
        if aspectRatio > thumbRatio:
            cropRatio = (width - (thumbRatio * height)) / width

            #all off the left
            if boundbox[2] > cropRatio and (1 - boundbox[3]) < cropRatio:
                left = width * cropRatio
                top = 0
                right = width
                bottom = height

            #all off the right
            elif boundbox[2] < cropRatio and (1 - boundbox[3]) > cropRatio:
                left = 0
                top = 0
                right = width - (1 - cropRatio)
                bottom = height

            #half off each side
            else:
                left = width * (0.5 * cropRatio)
                top = 0
                right = width * (1 - (0.5 * cropRatio))
                bottom = height


        #cut pixels off the top/bot
        if aspectRatio < thumbRatio:
            cropRatio = (height - (width / thumbRatio)) / height

            #half off both top/bot
            if boundbox[0] > (0.5 * cropRatio) and (1 - boundbox[1]) > (0.5 * cropRatio):
                left = 0
                top = height * (0.5 * cropRatio)
                right = width
                bottom = height * (1 - (0.5 * cropRatio))

            #all off the top
            elif boundbox[0] > cropRatio and (1 - boundbox[1]) < cropRatio:
                left = 0
                top = height * cropRatio
                right = width
                bottom = height

            #all off the bottom
            else:
                left = 0
                top = 0
                right = width
                bottom = height * (1 - cropRatio)

        left = int(left)
        top = int(top)
        right = int(right)
        bottom = int(bottom)
        
        im = im.crop((left, top, right, bottom))

        im = ImageOps.contain(im, (thumbWidth, thumbHeight))
        #end of my code

        im.save(in_mem_file, format='jpeg')
        in_mem_file.seek(0)
        photo = photo[7:]

        response = client.put_object(
            Body=in_mem_file,
            Bucket=des_bucket,
            Key="thumbs/" + photo,
            ContentType='image/jpeg'

        )

        del boundbox
        del file_byte_string
        del in_mem_file
        im.close()
        del im

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(photo, src_bucket.name))
        raise e


def detect_bounds(photo, bucket):

    client=boto3.client('rekognition')
    topratio = 1
    botratio = 0
    leftratio = 1
    rightratio = 0

    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)

    print('Detected labels for ' + photo) 
    print()   
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        print ("Instances:")
        for instance in label['Instances']:
            print ("  Bounding box")
            print ("    Top: " + str(instance['BoundingBox']['Top']))
            print ("    Left: " + str(instance['BoundingBox']['Left']))
            print ("    Width: " +  str(instance['BoundingBox']['Width']))
            print ("    Height: " +  str(instance['BoundingBox']['Height']))
            top = instance['BoundingBox']['Top']
            if top < topratio:
                topratio = top
            h = instance['BoundingBox']['Height']
            if h > botratio:
                botratio = h + top
            left = instance['BoundingBox']['Left']
            if left < leftratio:
                leftratio = left
            w = instance['BoundingBox']['Width']
            if w > rightratio:
                rightratio = w + left
            print()

        print ("Parents:")
        for parent in label['Parents']:
            print ("   " + parent['Name'])
        print ("----------")
        print ()
    
    boundbox = (topratio, botratio, leftratio, rightratio)
    print(boundbox)

    del response
    del label
    del instance
    del parent

    return boundbox





def lambda_handler(event, context):
    
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    body = json.loads(event['Records'][0]['body'])
    bucket = body['Records'][0]['s3']['bucket']['name']
    key = body['Records'][0]['s3']['object']['key']    

    print("BUCKET: " + bucket, "KEY: " + key)

    bucket = s3.Bucket(bucket)
    boundbox = detect_bounds(key, bucket.name)
    resize_image(bucket, key, boundbox, 'image-processing-kevin')