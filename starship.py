from bs4 import BeautifulSoup
import requests
import boto3
import json
import os

def handler(event, context):
    # set environment variables
    sn = os.environ['SN']
    mode = os.environ['MODE']

    # get web page
    url = 'https://everydayastronaut.com/when-will-sn' + sn + '-launch-live-updates/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # get current top-level update
    date_tag = soup.find('h3' ,id='h-live-updates').find_next('p')
    update_tag = date_tag.find_next('p')

    date = date_tag.get_text().strip()
    update = update_tag.get_text().strip()

    current_update = date + '\n\n' + update

    # get the latest update from s3
    bucket_name = "starship-updates"
    s3 = boto3.resource("s3")
    obj = s3.Object(bucket_name, 'latest-update')
    latest_update = obj.get()['Body'].read().decode('utf-8')

    # if updates are not the same, save newest update and send newest update to SNS
    if (latest_update != current_update or mode == 'debug'):
        encoded_string = current_update.encode("utf-8")
        s3.Bucket(bucket_name).put_object(Key='latest-update', Body=encoded_string)

        message = 'SN' + sn + ' Update\n\n' + current_update + '\n\nFrom ' + url + '.'

        client = boto3.client('sns')
        response = client.publish(
            TargetArn='arn:aws:sns:us-east-1:878228692056:starship-updates',
            Message=json.dumps({'default': message}),
            MessageStructure='json',
            Subject='Starship Update'
        )

        return message
    else: 
        return 'No updates'