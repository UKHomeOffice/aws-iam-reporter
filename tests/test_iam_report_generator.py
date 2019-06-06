"""Tests for the AWSAccountReportGenerator class
"""
import json
from unittest import TestCase

import boto3
from moto import mock_iam
import iam_report_generator


@mock_iam
class IamReportGeneratorTest(TestCase):
    """Class for testing the AWSAccountReportGenerator methods
    """

    def setUp(self):
        """Sets up fixtures for the tests

        :return: None
        """
        self.my_managed_policy = {
            "Version": "2012-10-17",
            "Statement": [
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

        self.assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {
                    "Service": "organizations.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }]
        }

    def test_iam_report_created(self):
        """Test the content of the IAM report

        :return: None
        """
        # Given
        iam = boto3.client("iam")
        user_name = "TEST_USER"
        iam.create_user(
            UserName=user_name
        )

        response = iam.create_policy(
            PolicyName="budget-alerting-management",
            PolicyDocument=json.dumps(self.my_managed_policy)
        )
        policy_arn = response["Policy"]["Arn"]

        iam.attach_user_policy(
            UserName=user_name,
            PolicyArn=policy_arn
        )

        response = iam.create_role(
            Path="/aws-service-role/dynamodb.application-autoscaling.amazonaws.com/",
            RoleName="AWSServiceRoleForApplicationAutoScaling_DynamoDBTable",
            AssumeRolePolicyDocument=json.dumps(self.assume_role_policy_document)
        )
        expected_role_id = response["Role"]["RoleId"]
        expected_role_arn = response["Role"]["Arn"]

        # When
        json_report = iam_report_generator.AWSAccountReportGenerator.generate_report()

        # Then
        data = json.loads(json_report)
        assert len(data["users"]) == 1
        assert data["users"][0]["user_name"] == "TEST_USER"
        user_policy = data["users"][0]["user_policy"]
        assert user_policy["default_version_id"] == "v1"

        assert len(user_policy["statements"]) == 2

        assert user_policy["statements"][0]["Effect"] == "Allow"
        assert user_policy["statements"][0]["Action"] == "logs:CreateLogGroup"
        assert user_policy["statements"][0]["Resource"] == "RESOURCE_ARN"

        assert user_policy["statements"][1]["Effect"] == "Allow"
        assert len(user_policy["statements"][1]["Action"]) == 5

        assert user_policy["statements"][1]["Action"][0] == "dynamodb:DeleteItem"
        assert user_policy["statements"][1]["Action"][1] == "dynamodb:GetItem"
        assert user_policy["statements"][1]["Action"][2] == "dynamodb:PutItem"
        assert user_policy["statements"][1]["Action"][3] == "dynamodb:Scan"
        assert user_policy["statements"][1]["Action"][4] == "dynamodb:UpdateItem"

        assert user_policy["statements"][1]["Resource"] == "RESOURCE_ARN"

        assert len(data["roles"]) == 1
        assert data["roles"][0]["path"] \
            == "/aws-service-role/dynamodb.application-autoscaling.amazonaws.com/"
        assert data["roles"][0][
            "role_name"] == "AWSServiceRoleForApplicationAutoScaling_DynamoDBTable"
        assert data["roles"][0]["role_id"] == expected_role_id
        assert data["roles"][0]["arn"] == expected_role_arn
        assert data["roles"][0][
            "assume_role_policy_document"] == self.assume_role_policy_document
