from bs4 import BeautifulSoup
import requests
import boto3
import json
import os
import re
from functools import reduce

def format_update(date, details):
    return date + ':\n' + details

def format_message(updates):
    n = str(len(updates))
    return 'There are ' + n + ' new updates:\n\n' + reduce(lambda x,y: x + '\n\n' + y, updates[::-1])

def save_to_bucket(update, bucket_name, key):
    encoded_string = update.encode("utf-8")
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=key, Body=encoded_string)

def send_sns(message):
    message = message
    client = boto3.client('sns')
    response = client.publish(
        TargetArn='arn:aws:sns:us-east-1:878228692056:starship-updates-dev',
        Message=json.dumps({'default': message}),
        MessageStructure='json',
        Subject='Starship Update'
    )

def handler(event, context):

    # set environment variables
    sn = os.environ['SN']

    try:
        s3 = boto3.resource("s3")
        obj = s3.Object('starship-updates', 'latest-update-dev')
        latest_update = obj.get()['Body'].read().decode('utf-8')
    except:
        latest_update = None

    # get web page
    url = 'https://everydayastronaut.com/when-will-sn' + sn + '-launch-live-updates/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # get current top-level update
    updates = soup.find('h3' ,id='h-live-updates').find_all_next('p')
    updates = [ele.get_text().strip() for ele in updates]
    updates_formatted = [format_update(i,j) for i,j in zip(updates[::2], updates[1::2])] 

    ex = r'^\D*\s\d{2},\s\d{4}\s~\s\d{2}:\d{2}\sUTC\s'
    updates_formatted = list(filter(lambda x: re.match(ex, x), updates_formatted))

    if (latest_update):
        newest_updates = updates_formatted[:updates_formatted.index(latest_update)]
        if (newest_updates):
            save_to_bucket(updates_formatted[0], 'starship-updates', 'latest-update-dev')
            message = format_message(newest_updates)
            send_sns(message)
            return message
        else: 
            return 'No new updates'
    else: # if no latest_update in S3, only send the top level update
        save_to_bucket(updates_formatted[0], 'starship-updates', 'latest-update-dev')
        message = format_message([updates_formatted[0]])
        send_sns(message)
        return message