import boto3
import os
import sys

# Create an SNS client
sns = boto3.client('sns')

email_topic = os.environ['mySNSTopic']

def send_notification(subject, body):
    try:
        response = sns.publish(
            TopicArn=email_topic,
            Subject = subject,
            Message=body
        )
        print(response)

    except Exception as e:
        print("SNS problem publishing message to Topic: " + email_topic)
        print("The reported problem was: " + str(e))
        sys.exit(1)