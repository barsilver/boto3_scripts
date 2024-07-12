#!/usr/bin/env python3

import os
import time
import boto3

def validate_env_vars():
    required_vars = ["ROLE_ARN", "SCHED", "RETENTION_PERIOD", "DEST_REGION"]
    for var in required_vars:
        if not os.environ.get(var):
            raise EnvironmentError(f"Environment variable {var} is not set.")

def list_namespaces(client):
    return [ns["namespaceName"] for ns in client.list_namespaces()["namespaces"]]

def list_scheduled_actions(client):
    return [sa["scheduledActionName"].replace("scheduledsnapshot-", "") 
            for sa in client.list_scheduled_actions()["scheduledActions"]]

def create_scheduled_action(client, namespace_name):
    client.create_scheduled_action(
        enabled=True,
        namespaceName=namespace_name,
        roleArn=os.environ["ROLE_ARN"],
        schedule={"cron": os.environ["SCHED"]},
        scheduledActionDescription="",
        scheduledActionName=f"scheduledsnapshot-{namespace_name.lower()}",
        targetAction={
            "createSnapshot": {
                "namespaceName": namespace_name,
                "retentionPeriod": int(os.environ["RETENTION_PERIOD"]),
                "snapshotNamePrefix": namespace_name,
            }
        },
    )
    print(f"Scheduled action created for {namespace_name}")

def create_snapshot_copy_configuration(client, namespace_name):
    client.create_snapshot_copy_configuration(
        namespaceName=namespace_name,
        snapshotRetentionPeriod=int(os.environ["RETENTION_PERIOD"]),
        destinationRegion=os.environ["DEST_REGION"],
    )
    print(f"Snapshot copy configuration created for {namespace_name}")

def handle_event(event, client):
    if not event:
        namespaces = list_namespaces(client)
        scheduled_actions = list_scheduled_actions(client)
        old_namespaces = [ns for ns in namespaces if ns not in scheduled_actions]

        for namespace in old_namespaces:
            try:
                create_scheduled_action(client, namespace)
                create_snapshot_copy_configuration(client, namespace)
            except Exception as e:
                print(f"Failed for {namespace}: {e}")

    else:
        event_record = event["detail"]
        namespace_name = event_record["responseElements"]["namespace"]["namespaceName"]

        if event_record["eventName"] == "DeleteNamespace":
            client.delete_scheduled_action(
                scheduledActionName=f"scheduledsnapshot-{namespace_name.lower()}"
            )
            print(f"Scheduled action deleted for {namespace_name}")

        elif event_record["eventName"] == "CreateNamespace":
            max_retries, retry_interval = 20, 30

            for attempt in range(max_retries):
                ns_details = client.get_namespace(namespaceName=namespace_name)
                status = ns_details["namespace"]["status"]

                if status != "AVAILABLE":
                    print(f"Attempt {attempt+1}/{max_retries}: Namespace is {status}, retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                else:
                    print(f"Namespace is {status}, creating scheduled action...")
                    try:
                        create_scheduled_action(client, namespace_name)
                        create_snapshot_copy_configuration(client, namespace_name)
                    except Exception as e:
                        print(f"Failed for {namespace_name}: {e}")
                    break
            else:
                print("Namespace did not become available within the expected time.")

def lambda_handler(event, context):
    validate_env_vars()
    client = boto3.client("redshift-serverless")
    handle_event(event, client)
