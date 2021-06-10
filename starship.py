from bs4 import BeautifulSoup
import requests
import boto3
import json
import re
from functools import reduce

def format_update(date, details):
    return date + ':\n' + details

def format_message(updates, env):
    n = str(len(updates))
    prefix = '(dev) ' if env == 'dev' else ''
    suffix = '\n\nFrom https://everydayastronaut.com/when-will-sn15-launch-live-updates/' if env == 'dev' else ''
    if (n == '1'):
        return prefix + 'There is ' + n + ' new update:\n\n' + reduce(lambda x,y: x + '\n\n' + y, updates[::-1]) + suffix
    else:
        return prefix + 'There are ' + n + ' new updates:\n\n' + reduce(lambda x,y: x + '\n\n' + y, updates[::-1]) + suffix

def save_to_bucket(update, bucket_name, key):
    encoded_string = update.encode("utf-8")
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=key, Body=encoded_string)

def send_sns(message, sns_arn):
    message = message
    client = boto3.client('sns')
    response = client.publish(
        TargetArn=sns_arn,
        Message=json.dumps({'default': message}),
        MessageStructure='json',
        Subject='Starship Update'
    )

def handler(event, context):
    # get input variables
    env = event['env']
    sn = event['sn']
    sns_id = event['sns_id']

    # set constants
    bucket_name = 'starship-updates'
    
    if (env == 'dev'):
        object_key = 'latest-update-dev'
        sns_arn = 'arn:aws:sns:us-east-1:' + sns_id + ':starship-updates-dev'
    else:
        object_key = 'latest-update'
        sns_arn = 'arn:aws:sns:us-east-1:' + sns_id + ':starship-updates'

    try:
        s3 = boto3.resource("s3")
        obj = s3.Object(bucket_name, object_key)
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

    ex = r'^\D*\s\d{1,2},\s\d{4}\s?~\s?\d{2}:\d{2}\sUTC\s'
    updates_formatted = list(filter(lambda x: re.match(ex, x), updates_formatted))

    if (latest_update):
        try:
            newest_updates = updates_formatted[:updates_formatted.index(latest_update)]
        except:
            newest_updates = [updates_formatted[0]]
        if (newest_updates):
            save_to_bucket(updates_formatted[0], bucket_name, object_key)
            message = format_message(newest_updates, env)
            send_sns(message, sns_arn)
            return message
        else: 
            return 'No new updates'
    else: # if no latest_update in S3, only send the top level update
        save_to_bucket(updates_formatted[0], bucket_name, object_key)
        message = format_message([updates_formatted[0]], env)
        send_sns(message, sns_arn)
        return message