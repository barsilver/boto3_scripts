# Redshift Serverless Snapshot Scheduler Tool

## Overview

The Redshift Serverless Snapshot Scheduler Tool is a command-line interface (CLI) designed to simplify the management of snapshot schedules for Amazon Redshift Serverless namespaces. It provides commands to create, update, delete snapshot schedules, and restore namespaces from snapshots.

This tool was created to address the need for managing snapshot schedules for Redshift Serverless namespaces. At present, the creation and management of these schedules are not directly supported by the Terraform AWS provider. Therefore, this tool serves as a temporary solution until the necessary resources are added to Terraform.

## Purpose

- **Temporary Solution**: As of now, the Terraform AWS provider does not support the direct management of snapshot schedules for Redshift Serverless namespaces. This tool fills that gap by providing a simple CLI for managing these schedules.
- **Ease of Use**: The tool simplifies the process of creating, updating, and deleting snapshot schedules, allowing users to perform these operations easily from the command line.
- **Snapshot Restoration**: Additionally, the tool offers functionality to restore namespaces from snapshots, facilitating recovery and maintenance tasks.
- **AWS CLI Alternative**: While these operations can be performed using the AWS CLI, this tool simplifies the process by providing only the relevant parameters and default values that apply to our project's needs.

## Usage

### Prerequisites

Before using the Redshift Serverless Snapshot Scheduler Tool, ensure you have:

- Python 3.x installed on your system.
- The necessary libraries installed. You can install them using the following command:

    ```bash
    pip3 install -r requirements.txt
    ```

- **AWS Credentials**: Configure AWS credentials with the necessary permissions. Ensure that the relevant SSO profile is connected to the AWS account you'd like to apply the code to.

- **IAM Policy**: The IAM role used should have the following IAM policy attached:

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "redshift-serverless:CreateScheduledAction",
                    "redshift-serverless:UpdateScheduledAction",
                    "redshift-serverless:DeleteScheduledAction",
                    "redshift-serverless:CreateSnapshot",
                    "redshift-serverless:CreateSnapshotCopyConfiguration",
                    "redshift-serverless:UpdateSnapshotCopyConfiguration",
                    "redshift-serverless:DeleteSnapshotCopyConfiguration"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:redshift-serverless:*:<AWS_ACCOUNT_ID>:namespace/*",
                    "arn:aws:redshift-serverless:*:<AWS_ACCOUNT_ID>:snapshot/*"
                ]
            }
        ]
    }
    ```

- **Trust Relationship**: The IAM role used should have a trust relationship allowing the Redshift service to assume the role. Here's an example trust relationship:

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "scheduler.redshift.amazonaws.com",
                        "redshift-serverless.amazonaws.com"
                    ]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    ```

### Installation

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/barsilver/redshift-serverless-scheduler.git
    ```

2. Navigate to the project directory:

    ```bash
    cd redshift-serverless-scheduler
    ```

### Commands

The Redshift Serverless Snapshot Scheduler Tool supports the following commands:

- **create**: Create a snapshot schedule for a Redshift Serverless namespace.
- **update**: Update an existing snapshot schedule for a Redshift Serverless namespace.
- **delete**: Delete an existing snapshot schedule for a Redshift Serverless namespace.
- **restore**: Restore a Redshift Serverless namespace from a snapshot.

For detailed usage instructions and options for each command, refer to the command-line help:

```bash
./redshiftserverless_scheduler.py <command> --help
```