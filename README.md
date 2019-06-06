# aws-iam-reporter

A python script that downloads iam reports mapping all the IAM roles and permissions within an AWS account and creates a single IAM report for the account in JSON format.


# Sample report

``` json
{
    "users": [
        {
            "user_name": "TEST_USER",
            "create_date": "2019-06-04 09:32:25+00:00",
            "user_policy": {
                "default_version_id": "v1",
                "statements": [
                    {
                        "Effect": "Allow",
                        "Action": "logs:CreateLogGroup",
                        "Resource": "RESOURCE_ARN"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "dynamodb:DeleteItem",
                            "dynamodb:GetItem",
                            "dynamodb:PutItem",
                            "dynamodb:Scan",
                            "dynamodb:UpdateItem"
                        ],
                        "Resource": "RESOURCE_ARN"
                    }
                ]
            }
        }
    ],
    "roles": [
        {
            "path": "/aws-service-role/dynamodb.application-autoscaling.amazonaws.com/",
            "role_name": "AWSServiceRoleForApplicationAutoScaling_DynamoDBTable",
            "role_id": "yil0tryle6jzsz71dp25",
            "arn": "arn:aws:iam::123456789012:role/aws-service-role/dynamodb.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_DynamoDBTable",
            "create_date": "2019-06-04 09:32:25.960729+00:00",
            "assume_role_policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "organizations.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "max_session_duration": 3600
        }
    ]
}
```

Command to run the script

`python iam_report_generatore.py`

The script prints the report in the console.