import boto3

s3 = boto3.resource('s3')
client = boto3.client('s3')

def lambda_handler(event, context):

    
    bucket = 'image-processing-kevin'
    bucket = s3.Bucket(bucket)

    #build list of keys for objects with thumbs/ prefix
    key = []
    for obj in bucket.objects.filter(Prefix='thumbs/'):
        key.append(obj.key)
    if len(key) == 1:
        #break due to finding just the prefix folder
        pass
    else:
        #build list of TagInfo for list of images
        key = key[1:]
        getTagResponse = []
        for item in key:
            getTagResponse.append(client.get_object_tagging(
            Bucket=bucket.name,
            Key=item,
            ))

        #get current production image count
        prod = 1
        for img in getTagResponse:
            for tag in img['TagSet']:
                if ('Key', 'prod') in tag.items():
                    prod += 1
        good = None
        live = None
        myDict = {}
        #check each image for tags of state and prod
        for img in getTagResponse:
            for tag in img['TagSet']:
                if ('Key', 'state') in tag.items() and ('Value', 'good') in tag.items():
                    good = True
                elif ('Key', 'prod') in tag.items():
                    live = True
                else:
                    pass
            if good is True and live is not True:
                newKey = ('Key', 'prod')
                newValue = ('Value', str(prod))
                tmpList = [newKey, newValue]
                tmpDict = dict(tmpList)
                img['TagSet'].append(tmpDict)
                myDict[getTagResponse.index(img)] = img['TagSet']
                prod += 1
                good = None
                live = None
        
        prefix = ('fulls', 'thumbs')
        nakedKey = []
        for var in key:
            nakedKey.append(var[7:])

        for each in nakedKey:
            if nakedKey.index(each) in myDict:
                for i in prefix:
                    print(myDict[nakedKey.index(each)])
                    print('{}/{}'.format(i, each))
                    putTagResponse = client.put_object_tagging(
                    Bucket='image-processing-kevin',
                    Key='{}/{}'.format(i, each),
                    Tagging={
                        'TagSet': myDict[nakedKey.index(each)]
                        },
                    )
            else:
                print('Key not found in myDict: '+str(each))


        # if len(getTagResponse[0]['TagSet']) > 0:
        #     pass #if has tags evaluate
        # elif len(getTagResponse[0]['TagSet']) < 0:
        #     pass #if no tags do nothing



            # tagSet = getTagResponse['TagSet']
            # for tag in tagSet:
            #     if 'state' in tag.values():
            #         #check state and live status
            #         print('STATE FOUND: '+str(tag['Value']))
            #     else:
            #         print('STATE NOT FOUND FOR '+str(key[item]))



