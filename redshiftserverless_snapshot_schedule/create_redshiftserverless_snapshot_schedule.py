import boto3
import argparse

def create_scheduled_action(client, enabled, namespace_name, role_arn, schedule, description, action_name, target_action):
    response = client.create_scheduled_action(
        enabled=enabled,
        namespaceName=namespace_name,
        roleArn=role_arn,
        schedule=schedule,
        scheduledActionDescription=description,
        scheduledActionName=action_name,
        targetAction=target_action
    )
    return response

def parse_arguments():
    parser = argparse.ArgumentParser(description='Create a scheduled action for Redshift Serverless.')
    parser.add_argument('--namespace-name', required=True, help='Name of the Redshift Serverless namespace')
    parser.add_argument('--role-arn', default='default-role-arn', help='ARN of the IAM role for the scheduled action (default: default-role-arn)')
    parser.add_argument('--description', help='Description for the scheduled action')
    parser.add_argument('--sso-profile', required=True, help='SSO AWS profile name')
    return parser.parse_args()

def main():
    args = parse_arguments()

    # Create a Redshift Serverless client with the specified AWS profile
    session = boto3.Session(profile_name=args.sso_profile)
    redshift_serverless_client = session.client('RedshiftServerless', region_name='your-region')

    default_action_name = f"DailySnapshot-{args.namespace_name}"
    default_schedule = ''
    default_retention_period = 7
    default_target_action = f'''
        {{
            "createSnapshot": {{
                "namespaceName": "{args.namespace_name}",
                "retentionPeriod": {default_retention_period},
                "snapshotNamePrefix": "{args.namespace_name}"
            }}
        }}
    '''

    response = create_scheduled_action(
        client=redshift_serverless_client,
        enabled=True,
        namespace_name=args.namespace_name,
        role_arn=args.role_arn,
        schedule={'cron': default_schedule},
        description=args.description,
        action_name=default_action_name,
        target_action=default_target_action
    )

    print(response)

if __name__ == "__main__":
    main()
