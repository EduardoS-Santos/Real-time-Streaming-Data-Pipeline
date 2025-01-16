# Real-time-Streaming-Data-Pipeline

Server

  This Ubuntu 20.04.6 server is designed to store real-time messages related to subscription renewals for a producer, publishing them to a topic and consuming them on demand with a consumer. The messages are then sent as JSON files to an S3 bucket on AWS. A trigger in S3 activates an AWS Lambda function that processes the data, removing duplicates and null values, and saves the cleaned data into MongoDB for further analysis using MongoDB Charts.

Server Specifications

  This server includes the following:

- Java 8
- Kafka
- SSH
- Python

Note:
The installation scripts should be in separate files, following this preferred order: SSH - Java- Kafka - Python

- Python Libraries Installed
- kafka-python
- Faker
- Boto3


AWS Infrastructure
  A bucket named dadosbrutosparatratamento was created in S3. Inside the bucket, a folder contains a trigger that detects the addition of new .json files, activating the Lambda function.

IAM Configurations
  In AWS IAM, a group for consumers was created with the AmazonS3FullAccess permission. A user was then created and added to this group.

  Additionally, a separate IAM role for the AWS Lambda service was created with the following permissions:

'AmazonS3FullAccess'
'AmazonS3ObjectLambdaExecutionRolePolicy'
'AmazonS3OutpostsFullAccess'
'AmazonS3ReadOnlyAccess'
'CloudWatchLogsFullAccess'
'SecretsManagerReadWrite'

This role allows access to external applications.

In the AWS Lambda console, a Lambda function was created and assigned the IAM role mentioned above. A custom layer was added, containing the required Python libraries (Linux distribution) for Python version 3.11. This layer is accessible from a compressed folder uploaded to the S3 bucket.

Tests
After completing the setup, the Lambda function was deployed, and tests were conducted using the on-premise environment. Approximately 100,000 messages were produced, consumed in blocks of 10,000 messages, converted to JSON, and sent to S3.
