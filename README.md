# Redshift Serverless Snapshot Scheduler Tool

## Overview

The Lambda function automates the creation of a scheduled action ("CreateSnapshot") and configures cross-region snapshot copying whenever a new namespace is created in Redshift Serverless. This temporary solution addresses the current limitation in the AWS Terraform Provider, which does not support creating scheduled actions directly. The function ensures that every new namespace is equipped with a scheduled snapshot and a cross-region copy configuration, enhancing data durability and disaster recovery.

This function was created to address the need for managing snapshot schedules for Redshift Serverless namespaces. At present, the creation and management of these schedules are not directly supported by the Terraform AWS provider. Therefore, this tool serves as a temporary solution until the necessary resources are added to Terraform.

## Resources Required

To ensure the Lambda function operates correctly, several AWS resources and configurations are necessary:

- **IAM Role**: The IAM Role provides the necessary permissions for the Lambda function to interact with AWS services, allowing it to create scheduled actions, snapshots, and snapshot copy configurations in Redshift Serverless. It also grants access to CloudWatch Logs for logging purposes.

- **IAM Policy**: The IAM Policy defines the permissions granted to the IAM role for managing scheduled actions and snapshots in Redshift Serverless, as well as Cloudwatch logs from the Lambda function.

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
            "redshift-serverless:ListSnapshotCopyConfigurations",
            "redshift-serverless:DeleteSnapshotCopyConfiguration",
            "redshift-serverless:ListNamespaces",
            "redshift-serverless:ListScheduledActions",
            "redshift-serverless:GetNamespace"
        ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:redshift-serverless:*:${local.account_id}:namespace/*",
            "arn:aws:redshift-serverless:*:${local.account_id}:snapshot/*",
            "arn:aws:redshift-serverless:*:${local.account_id}:scheduledaction/*"
        ]
        },
        {
        "Action": [
            "logs:CreateLogGroup"
        ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:logs:${local.region}:${local.account_id}:*"
        ]
        },
        {
        "Action": [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.deployment_name}-${var.environment}-${data.aws_region.current.name}:*"
        ]
        }
    ]
    }
    ```

- **Trust Relationship**: The trust relationship allows services like Redshift Scheduler, Redshift Serverless, and Lambda to assume the IAM role.
This trust relationship enables the Redshift scheduler (scheduler.redshift.amazonaws.com) to assume this IAM role to schedule snapshots, and the lambda.amazonaws.com to log to CloudWatch Logs.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                "scheduler.redshift.amazonaws.com",
                "redshift-serverless.amazonaws.com",
                "lambda.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole"
            }
        ]
        }
    ```

## Trigger
The trigger is configured to invoke the Lambda function whenever a new namespace is created in Redshift Serverless. It is set up as a CloudWatch Events rule.

### Configuration
- **Event Source**: Redshift Serverless namespace creation and namespace deletion events
- **Target**: Lambda function ARN
    ```json
    {
    "source": ["aws.redshift-serverless"],
    "detail": {
        "eventSource": ["redshift-serverless.amazonaws.com"],
        "eventName": ["CreateNamespace", "DeleteNamespace"]
    }
    }
    ```
This configuration captures each Redshift Serverless namespace creation event and triggers the specified Lambda function to handle the snapshot scheduling and cross-region copy configuration. Additionally, it captures delete namespace events, triggering the Lambda function to delete the scheduled action if a namespace deletion occurs, ensuring proper clean-up.

## Lambda Function
The Lambda function automates the creation of a snapshot schedule and configures cross-region snapshot copying. It reads the namespace creation event, configures the snapshot schedule, and sets up the necessary copy configuration.

### Environment Variables
Refer to the Terraform code for the exact lines where these variables are being set.

`SCHED`: Schedule invocations must be separated by at least one hour.
Format of cron expression is `"Minutes Hours Day-of-month Month Day-of-week Year"`.
Default value: `"0 0,8,16 * * ? *"`. Defaults to running every 8 hours.

`ROLE_ARN`: The ARN of the IAM role to assume to run the scheduled action.
The lambda function configuration and the code must use the same IAM role to prevent an AccessDeniedException error. The IAM role is created as part of the Lambda module in Terraform.

`RETENTION_PERIOD`: The retention period of the snapshot created by the scheduled action.
Default value: `7`.

`DEST_REGION`: The region to which snapshots will be copied.
No default value. This variable must be set.

### Manual Execution and Event Handling
To run the Lambda function manually, you can invoke it with an empty event ({}). This will trigger the if not event section of the Lambda code, where it lists all namespaces and scheduled actions, identifies namespaces without scheduled actions, and creates the necessary scheduled actions and cross-region copy configurations for those namespaces.

**Steps to run the function manually:**

 Enter the lambda function in the relevant region.

1. Click on the Test tab.

2. Edit the Event JSON so it will only contain `{}`.

3. Run the test event.

 After running the test, you can check the CloudWatch logs to verify which scheduled actions were created and to which namespaces they were assigned.

 ### Namespace Status Check Loop
 When a new namespace is created, the Lambda function includes a loop that retries to check the namespace status. This loop will attempt to check the namespace status up to 20 times, with a 30-second interval between retries. The function will only proceed to create the scheduled actions and snapshot copy configuration once the namespace status is `AVAILABLE`. This ensures that all necessary resources are created only after the namespace is fully available.