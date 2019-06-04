import boto3
import os
import json


class AWSAccountReportGenerator(object):

    """Generates an AWS IAM report in JSON format"""

    def __init__(self):
        self.output_folder = os.environ["OUTPUT_FOLDER"]

    def generate_report(self):
        iam = {}
        AWSAccountReportGenerator.get_all_users_with_attached_policies(iam)
        AWSAccountReportGenerator.get_all_roles(iam)
        self.create_json_report(iam)


    @classmethod
    def get_all_users_with_attached_policies(cls, iam):
        # Gets all users along with their attached policies and sets the result as dictionary in 'iam'

        # Create an IAM service resource
        resource = boto3.resource("iam")
        # Get an iterable of all users
        users = resource.users.all()
        data = []

        for user in users:
            user_data = {"user_name": user.user_name, "create_date": user.create_date}

            user_attached_policies = user.attached_policies.all()

            user_policy_data = {}
            for user_policy in user_attached_policies:
                user_policy_data["default_version_id"] = user_policy.default_version_id
                stmts = user_policy.default_version.document.get("Statement")
                stmt_data = []
                for stmt in stmts:
                    stmt_data.append(stmt)

                user_policy_data["statements"] = stmt_data
                user_data["user_policy"] = user_policy_data

            data.append(user_data)

        iam["users"] = data

    @classmethod
    def get_all_roles(cls, iam):
        # Gets all roles and sets the result as dictionary in 'iam'

        resource = boto3.resource("iam")
        roles = resource.roles.all()

        data = []

        for role in roles:
            role_data = {"path": role.path, "role_name": role.role_name, "role_id": role.role_id, "arn": role.arn,
                         "create_date": role.create_date,
                         "assume_role_policy_document": role.assume_role_policy_document,
                         "max_session_duration": role.max_session_duration}
            data.append(role_data)

        iam["roles"] = data

    def create_json_report(self, iam):
        # create a report in JSON format and write that to output_folder
        json_dump = json.dumps(iam, indent=4, sort_keys=False, default=str)
        with open("{}/iam_report.json".format(self.output_folder), "w") as f:
            f.write(json_dump)


if __name__ == "__main__":
    AWSAccountReportGenerator().generate_report()
