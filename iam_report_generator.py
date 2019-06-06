"""Class generating an IAM report of users, roles, policies, etc for a given AWS account
"""
import json
import boto3


class AWSAccountReportGenerator:
    """Generates an AWS IAM report in JSON format
    """

    @classmethod
    def generate_report(cls):
        """Generate the IAM report

        :return: String - iam report as string in json format
        """
        users = AWSAccountReportGenerator.get_all_users_with_attached_policies()
        roles = AWSAccountReportGenerator.get_all_roles()
        iam = {"users": users, "roles": roles}
        return json.dumps(iam, indent=4, sort_keys=False, default=str)

    @classmethod
    def get_all_users_with_attached_policies(cls):
        """
        Gets all users along with their attached policies and sets the result as dictionary in 'iam'

        :param iam: a dictionary that is going to be populated with IAM user data
        :return: list of users with their attached policies
        """

        # Create an IAM service resource
        resource = boto3.resource("iam")
        # Get an iterable of all users
        users = resource.users.all()
        user_list = []

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

            user_list.append(user_data)

        return user_list

    @classmethod
    def get_all_roles(cls):
        """Gets all the roles defined in the current AWS account

        :param iam: a dictionary that is going to be populated with roles details
        :return: list of roles
        """
        # Gets all roles and sets the result as dictionary in 'iam'

        resource = boto3.resource("iam")
        roles = resource.roles.all()

        roles_list = []

        for role in roles:
            role_data = {"path": role.path, "role_name": role.role_name, "role_id": role.role_id,
                         "arn": role.arn,
                         "create_date": role.create_date,
                         "assume_role_policy_document": role.assume_role_policy_document,
                         "max_session_duration": role.max_session_duration}
            roles_list.append(role_data)

        return roles_list


if __name__ == "__main__":
    print(AWSAccountReportGenerator.generate_report())
