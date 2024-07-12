locals {
  deployment_version = "0.0.12"
  deployment_name    = "redshift-serverless-scheduler"
  account_id         = data.aws_caller_identity.current.account_id
  region             = data.aws_region.current.name
}

data "artifactory_file" "build" {
  repository  = var.artifactory_repo
  path        = var.artifactory_file_path
  output_path = "${path.module}/${local.deployment_name}-${local.deployment_version}.zip"
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

module "redshift_serverless_scheduler_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.10.1"

  function_name                 = "${local.deployment_name}-${data.aws_region.current.name}"
  runtime                       = var.runtime
  publish                       = false
  architectures                 = ["x86_64"]
  package_type                  = "Zip"
  handler                       = "code.lambda_handler"
  create_package                = false
  local_existing_package        = data.artifactory_file.build.output_path
  timeout                       = 30
  lambda_role                   = aws_iam_role.redshiftserverless_snapshot_scheduler_role.arn
  create_role                   = false
  attach_cloudwatch_logs_policy = false

  environment_variables = {
    DEST_REGION      = var.dest_region
    RETENTION_PERIOD = var.retention_period
    ROLE_ARN         = "${aws_iam_role.redshiftserverless_snapshot_scheduler_role.arn}"
    SCHED            = var.schedule
  }

  tags = {
    region = data.aws_region.current.name
  }
}

resource "aws_cloudwatch_event_rule" "namespace_creation_lambda_event_rule" {
  name        = "namespace-creation-lambda-event-rule"
  description = "Capture each Redshift Serverless namespace creation"
  event_pattern = jsonencode({
    source = ["aws.redshift-serverless"]
    detail = {
      eventSource = ["redshift-serverless.amazonaws.com"]
      eventName   = ["CreateNamespace", "DeleteNamespace"]
    }
  })
}

resource "aws_cloudwatch_event_target" "namespace_creation_lambda_target" {
  arn  = module.redshift_serverless_scheduler_lambda.lambda_function_arn
  rule = aws_cloudwatch_event_rule.namespace_creation_lambda_event_rule.name
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.redshift_serverless_scheduler_lambda.lambda_function_arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.namespace_creation_lambda_event_rule.arn
}

data "aws_iam_policy_document" "redshiftserverless_snapshot_scheduler_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = [
        "scheduler.redshift.amazonaws.com",
        "redshift-serverless.amazonaws.com",
        "lambda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "redshiftserverless_snapshot_scheduler_policy" {
  statement {
    actions = [
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
    ]
    resources = [
      "arn:aws:redshift-serverless:*:${local.account_id}:namespace/*",
      "arn:aws:redshift-serverless:*:${local.account_id}:snapshot/*",
      "arn:aws:redshift-serverless:*:${local.account_id}:scheduledaction/*"
    ]
    effect = "Allow"
  }
  statement {
    actions   = ["logs:CreateLogGroup"]
    resources = ["arn:aws:logs:${local.region}:${local.account_id}:*"]
    effect    = "Allow"
  }
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.deployment_name}-${data.aws_region.current.name}:*"]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "redshiftserverless_snapshot_scheduler_policy" {
  name   = "redshiftserverless_snapshot_scheduler_policy"
  policy = data.aws_iam_policy_document.redshiftserverless_snapshot_scheduler_policy.json
}

resource "aws_iam_role" "redshiftserverless_snapshot_scheduler_role" {
  name               = "redshiftserverless_snapshot_scheduler_role"
  assume_role_policy = data.aws_iam_policy_document.redshiftserverless_snapshot_scheduler_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "redshiftserverless_snapshot_scheduler_attachment" {
  role       = aws_iam_role.redshiftserverless_snapshot_scheduler_role.name
  policy_arn = aws_iam_policy.redshiftserverless_snapshot_scheduler_policy.arn
}