terraform {
  required_providers {
    artifactory = {
      source  = "registry.terraform.io/jfrog/artifactory"
      version = "~> 2.2.15"
    }
  }
}

provider "artifactory" {
  url           = "${var.artifactory_url}/artifactory"
  access_token  = "${var.artifactory_access_token}"
}