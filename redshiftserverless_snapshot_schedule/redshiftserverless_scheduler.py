#!/usr/bin/env python3

import boto3
import click
import botocore

@click.group()
def cli():
    """Redshift Serverless Snapshot Scheduler Tool"""


@cli.command(name='create')
@click.option('--namespace-name', required=True, help='Name of the Redshift Serverless namespace')
@click.option('--role-arn', default='<default-role-arn>', help='ARN of the IAM role for the scheduled action (default: <default-role-arn>)')
@click.option('--description', default='', help='Description for the scheduled action')
@click.option('--sso-profile', required=True, help='SSO AWS profile name')
@click.option('--schedule', default='0 19 * * ? *', help='Cron expression specifying the schedule for the Redshift Serverless snapshot creation. Defaults to running every day at 19:00 (7:00 PM).')
@click.option('--retention-period', default=7, type=int, help='Retention period for the snapshots in days (default: 7)')
@click.option('--action-name', default='', help='Name of the scheduled action (default: auto-generated)')
def create(namespace_name, role_arn, description, sso_profile, schedule):
    """Create snapshot schedule"""
    
    # Your existing logic for creating snapshot schedules here
    session = boto3.Session(profile_name=sso_profile)
    redshift_serverless_client = session.client('redshift-serverless')
    
    # If action_name is not provided, generate a default one
    if not action_name:
        action_name = f"dailysnapshot-{namespace_name.lower()}"

    default_target_action = {
        "createSnapshot": {
            "namespaceName": namespace_name,
            "retentionPeriod": retention_period,
            "snapshotNamePrefix": namespace_name
        }
    }

    try:
        response = create_scheduled_action(
            client=redshift_serverless_client,
            enabled=True,
            namespace_name=namespace_name,
            role_arn=role_arn,
            schedule={'cron': f"({schedule})"},
            description=description,
            action_name=action_name,
            target_action=default_target_action
        )

        scheduled_action_details = response.get('scheduledAction', {})

        if scheduled_action_details:
            print("Scheduled action created successfully!")
            print(f"Namespace Name: {scheduled_action_details['namespaceName']}")
            print(f"Scheduled Action Name: {scheduled_action_details['scheduledActionName']}")
            print(f"Next Invocations: {scheduled_action_details['nextInvocations']}")
            print(f"State: {scheduled_action_details['state']}")
        else:
            print("Scheduled action creation failed.")

    except botocore.exceptions.ParamValidationError as e:
        print(f"Error: {e}")


@cli.command(name='update')
@click.option('--namespace-name', required=True, help='Name of the Redshift Serverless namespace')
@click.option('--role-arn', default='<default-role-arn>', help='ARN of the IAM role for the scheduled action (default: <default-role-arn>)')
@click.option('--description', default='', help='Description for the scheduled action')
@click.option('--sso-profile', required=True, help='SSO AWS profile name')
@click.option('--schedule', default='0 19 * * ? *', help='Cron expression specifying the schedule for the Redshift Serverless snapshot update. Defaults to running every day at 19:00 (7:00 PM).')
@click.option('--retention-period', default=7, type=int, help='Retention period for the snapshots in days (default: 7)')
@click.option('--action-name', default='', help='Name of the scheduled action (default: auto-generated)')
def update(namespace_name, role_arn, description, sso_profile, schedule):
    """Update snapshot schedule"""
    
    # Your logic for updating snapshot schedules here
    session = boto3.Session(profile_name=sso_profile)
    redshift_serverless_client = session.client('redshift-serverless')
    
    # If action_name is not provided, generate a default one
    if not action_name:
        action_name = f"dailysnapshot-{namespace_name.lower()}"

    default_target_action = {
        "updateSnapshot": {
            "namespaceName": namespace_name,
            "retentionPeriod": retention_period,
            "snapshotNamePrefix": namespace_name
        }
    }

    try:
        response = update_scheduled_action(
            client=redshift_serverless_client,
            enabled=True,
            namespace_name=namespace_name,
            role_arn=role_arn,
            schedule={'cron': f"({schedule})"},
            description=description,
            action_name=action_name,
            target_action=default_target_action
        )

        scheduled_action_details = response.get('scheduledAction', {})

        if scheduled_action_details:
            print("Scheduled action updated successfully!")
            print(f"Namespace Name: {scheduled_action_details['namespaceName']}")
            print(f"Scheduled Action Name: {scheduled_action_details['scheduledActionName']}")
            print(f"Next Invocations: {scheduled_action_details['nextInvocations']}")
            print(f"State: {scheduled_action_details['state']}")
        else:
            print("Scheduled action update failed.")

    except botocore.exceptions.ParamValidationError as e:
        print(f"Error: {e}")


@cli.command(name='delete')
@click.option('--namespace-name', required=True, help='Name of the Redshift Serverless namespace')
@click.option('--sso-profile', required=True, help='SSO AWS profile name')
@click.option('--action-name', default='', help='Name of the scheduled action (default: auto-generated)')
def delete(namespace_name, sso_profile):
    """Delete snapshot schedule"""
    
    # Your logic for deleting snapshot schedules here
    session = boto3.Session(profile_name=sso_profile)
    redshift_serverless_client = session.client('redshift-serverless')

    # If action_name is not provided, generate a default one
    if not action_name:
        action_name = f"dailysnapshot-{namespace_name.lower()}"

    try:
        response = delete_scheduled_action(
            client=redshift_serverless_client,
            action_name=action_name
        )

        if 'Error' not in response:
            print("Scheduled action deleted successfully!")
        else:
            print(f"Scheduled action deletion failed. Error: {response.get('Error')}")

    except botocore.exceptions.ParamValidationError as e:
        print(f"Error: {e}")
    except botocore.exceptions.ClientError as e:
            print(f"Scheduled action deletion failed. {e}")


def delete_scheduled_action(client, action_name):
    response = client.delete_scheduled_action(
        scheduledActionName=action_name
    )
    return response


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

def update_scheduled_action(client, enabled, namespace_name, role_arn, schedule, description, action_name, target_action):
    response = client.update_scheduled_action(
        enabled=enabled,
        namespaceName=namespace_name,
        roleArn=role_arn,
        schedule=schedule,
        scheduledActionDescription=description,
        scheduledActionName=action_name,
        targetAction=target_action
    )
    return response


@cli.command()
def default():
    """Default command for unrecognized commands"""
    print("Error: Unrecognized command. Use the --help option for usage information.")

if __name__ == "__main__":
    cli()
