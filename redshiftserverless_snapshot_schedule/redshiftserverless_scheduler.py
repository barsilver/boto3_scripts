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
@click.option('--schedule', default='0 19 * * ? *', help='Cron expression specifying the schedule for the Redshift Serverless snapshot creation (UTC). Defaults to running every day at 19:00 (7:00 PM).')
@click.option('--retention-period', default=7, type=int, help='Retention period for the snapshots in days (default: 7)')
@click.option('--action-name', default='', help='Name of the scheduled action (default: auto-generated)')
def create(namespace_name, role_arn, description, sso_profile, schedule, retention_period, action_name):
    """Create snapshot schedule"""
    
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
@click.option('--schedule', default='0 19 * * ? *', help='Cron expression specifying the schedule for the Redshift Serverless snapshot update (UTC). Defaults to running every day at 19:00 (7:00 PM).')
@click.option('--retention-period', default=7, type=int, help='Retention period for the snapshots in days (default: 7)')
@click.option('--action-name', default='', help='Name of the scheduled action (default: auto-generated)')
def update(namespace_name, role_arn, description, sso_profile, schedule, retention_period, action_name):
    """Update snapshot schedule"""
    
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
def delete(namespace_name, sso_profile, action_name):
    """Delete snapshot schedule"""
    
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


@cli.command(name='restore')
@click.option('--namespace-name', required=True, help='Name of the Redshift Serverless namespace')
@click.option('--sso-profile', required=True, help='SSO AWS profile name')
@click.option('--snapshot-name', required=True, help='Name of the snapshot to restore from')
@click.option('--workgroup-name', default='', help='Name of the Redshift Serverless workgroup (default: auto-generated)')
def restore(namespace_name, sso_profile, snapshot_name, workgroup_name):
    """Restore namespace from snapshot"""
    
    session = boto3.Session(profile_name=sso_profile)
    redshift_serverless_client = session.client('redshift-serverless')

    # If workgroup_name is not provided, use the generated default of the Redshift Serverless Terraform module
    if not workgroup_name:
        workgroup_name = f"{namespace_name}-workgroup"

    try:
        response = restore_from_snapshot(
            client=redshift_serverless_client,
            namespace_name=namespace_name,
            snapshot_name=snapshot_name,
            workgroup_name=workgroup_name
        )

        if 'namespace' in response:
            namespace_details = response['namespace']
            print("Namespace restored successfully!")
            print(f"Namespace Name: {namespace_details['namespaceName']}")
            print(f"Database Name: {namespace_details['dbName']}")
            print(f"IAM Roles: {namespace_details['iamRoles']}")
            print(f"Status: {namespace_details['status']}")
        else:
            print("Namespace restoration failed.")

    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == 'ResourceNotFoundException':
            if "snapshot" in str(e):
                print(f"Error: Snapshot '{snapshot_name}' not found.")
            elif "workgroup" in str(e):
                print(f"Error: Serverless workgroup '{workgroup_name}' not found.")
        elif error_code == 'ConflictException':
            print("Error: Restore is in progress. Please check your serverless state or retry later.")
        else:
            print(f"Error: {e}")


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
        roleArn=role_arn,
        schedule=schedule,
        scheduledActionDescription=description,
        scheduledActionName=action_name,
        targetAction=target_action
    )
    return response

def restore_from_snapshot(client, namespace_name, snapshot_name, workgroup_name):
    response = client.restore_from_snapshot(
        namespaceName=namespace_name,
        snapshotName=snapshot_name,
        workgroupName=workgroup_name,
    )
    return response


@cli.command()
def default():
    """Default command for unrecognized commands"""
    print("Error: Unrecognized command. Use the --help option for usage information.")

if __name__ == "__main__":
    cli()
