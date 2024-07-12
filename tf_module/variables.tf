#Artifactory Variables
variable "artifactory_url" {
  type        = string
  description = "The URL for the artifactory server."
}

variable "artifactory_access_token" {
  type        = string
  description = "The access token for the artifactory server."
}

variable "artifactory_repo" {
  type        = string
  description = "Repository where the function zip is stored"
}

variable "artifactory_file_path" {
  type        = string
  description = "Path in the artifactory where the function zip is stored"
}

variable "runtime" {
  type        = string
  description = "Identifier of the function's runtime"
  default     = "python3.12"
}

variable "name" {
  description = "IAM prefix"
  type        = string
  default     = "redshiftserverless_backups"
}

variable "dest_region" {
  description = "The region where the snapshots will be synced to"
  type        = string
}

variable "retention_period" {
  description = "The retention period of the snapshot created by the scheduled action."
  type        = number
  default     = 7
}

variable "schedule" {
  description = "Schedule invocations must be separated by at least one hour. Format of cron expression is 'Minutes Hours Day-of-month Month Day-of-week Year'. Defaults to running every hour."
  type        = string
  default     = "0 0 * * ? *"
}