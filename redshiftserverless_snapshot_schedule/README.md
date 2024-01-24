# Redshift Serverless Snapshot Schedule Creation (Temporary Solution)

## Overview

This document provides information on a script designed for creating snapshot schedules for Amazon Redshift Serverless namepsaces. The script automates the creation of scheduled actions for snapshot management and is intended for use immediately after creating a new namespace in Redshift Serverless.

### Limitation and Future Integration

**Important:** The script is a temporary solution due to the current limitation that the operation is only available within the AWS CLI and API. It specifically caters to creating snapshot schedules for an existing namespace and should be executed once the namespace is created. Future plans involve transitioning to a more comprehensive approach once the Terraform AWS provider incorporates the necessary resources.

## Solution Script

### Script Description

The script, named `create_redshiftserverless_snapshot_schedule.py`, is tailored for setting up snapshot schedules in Redshift Serverless.

### Prerequisites

1. Ensure you have Python installed on your machine.
2. Install the required Python packages by running:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your AWS CLI with AWS SSO credentials:

   ```bash
   aws sso login --profile <your-sso-profile>
   ```

   Replace `<your-sso-profile>` with your AWS SSO profile name.

### Usage

1. Clone this repository.

2. Make the create_redshiftserverless_snapshot_schedule.py script executable:

   ```bash
   chmod +x create_redshiftserverless_snapshot_schedule.py
   ```

3. Execute the script with the required arguments:

   ```bash
   ./create_redshiftserverless_snapshot_schedule.py --namespace-name <your-namespace> --sso-profile <your-sso-profile>
   ```

   Replace `<your-namespace>` and `<your-sso-profile>` with your actual values.

### IAM Role Permissions

The script utilizes an IAM role named `RedshiftServerlessSnapshotSchedulerRole` for execution. This IAM role is assumed by the Redshift scheduler and already includes the necessary permissions to create scheduled actions for snapshot management.

### Notes

- This script is a temporary measure and is expected to be superseded by a more comprehensive infrastructure-as-code solution in the future.
- Ensure that you have the appropriate permissions to execute the script and create IAM roles.
