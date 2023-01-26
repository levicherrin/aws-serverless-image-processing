import json
import boto3



s3 = boto3.resource('s3')
client = boto3.client('s3')


def lambda_handler(event, context):

    body = json.loads(event['Records'][0]['body'])
    srcBucket = body['Records'][0]['s3']['bucket']['name']
    srcKey = body['Records'][0]['s3']['object']['key']    
    
    print("BUCKET: " + srcBucket, "KEY: " + srcKey)
    try:
        getTagresponse = client.get_object_tagging(
            Bucket=srcBucket,
            Key=srcKey,
        )

        for tag in getTagresponse['TagSet']:
            if ('Key', 'prod') in tag.items():
                prod = tag['Value']
        

        nakedKey = srcKey[6:]  
        
        destKey = ('full-{}.jpg'.format(prod), 'thumb-{}.jpg'.format(prod))
        prefix = ('fulls', 'thumbs')

        for i, j in zip (prefix, destKey):
            copy_source = {
                'Bucket': srcBucket,
                'Key': "{}/{}".format(i, nakedKey)
            }
            destBucket = s3.Bucket('live-image-test')
            obj = destBucket.Object("images/{}/{}".format(i, j))
            obj.copy(copy_source)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(srcKey, srcBucket))
        raise e