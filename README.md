# Starship Notification System 🚀

## What is this?

A Starship notification system built using AWS Lambda, SNS, and S3 along with the Serverless Application Framework.

## But why?

Starship development and testing was happening at a rapid pace in the spring of 2021, but I didn't want to keep checking [everydayastronaut.com](https://everydayastronaut.com/) all the time for the lastest updates. So I built this serverless notification system that pulls data from [everydayastronaut.com](https://everydayastronaut.com/) at some time interval and sends a notification via text or email of the latest updates.

## How does it work?

Every hour, CloudWatch events triggers the lambda function to run in AWS, passing in three inputs - the environment, the Starship serial number, and the SNS resource ID. The lambda function first reaches out to AWS S3 to get the latest update, which was saved to S3 by a previous lambda invocation. Then the lambda gets the webpage with the updates from `https://everydayastronaut.com/when-will-sn##-launch-live-updates/` where the `##` indicate the Starship serial number. The lambda function parses the webpage with Beautiful Soup and compares the list of updates with the latest update from S3. Then the lambda function creates the list of new updates since the latest update, formats the message, and sends the message to SNS for delivery. It also saves the most recent updated from the webpage to S3 for future innovations to use.

## Used in this project

* [AWS Lambda](https://aws.amazon.com/lambda/)
* [AWS SNS](https://aws.amazon.com/sns/)
* [AWS S3](https://aws.amazon.com/s3/)
* [Servless Application Framework](https://www.serverless.com/)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## Acknowledgements

Thank you to [Tim Dodd the Everyday Astronaut](https://www.youtube.com/channel/UC6uKrU_WqJ1R2HMTY3LIx5Q) for always keeping us updated with the latest Starship and SpaceX news.



