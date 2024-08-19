#Variables
variable "infrastructure_version" {
  default = "1"
}
variable "access_key" {
  default = ""
}
variable "secret_key" {
  default = ""
}
variable "region" {
  default = "us-east-1"
}
variable "vpc_cidr" {
  description = "The CIDR Block for the SiteSeer VPC"
  default     = "10.0.0.0/16"
}

variable "rt_wide_route" {
  description = "Route in the SiteSeer Route Table"
  default     = "0.0.0.0/0"
}
variable "subnet_count" {
  description = "no of subnets"
  default = 2
}
variable "availability_zones" {
  description = "availability zone to create subnet"
  default = [
    "us-east-1a",
    "us-east-1b"]
}
variable "flask_app_port" {
  description = "Port exposed by the flask application"
  default = 9696
}
variable "flask_app_image" {
  description = "Dockerhub image for flask-app"
  default = "elvis5050/temp-model-pred:latest"
}
variable "flask_app" {
  description = "FLASK APP variable"
  default = "app"
}
variable "flask_env" {
  description = "FLASK ENV variable"
  default = "prod"
}
variable "flask_app_home" {
  description = "APP HOME variable"
  default = "/app/"
}
variable "ecs_task_definition_name" {
  description = "Task definition name."
  type = string
  default = "flask-app"
}

variable "cloudwatch_group" {
  description = "CloudWatch group name."
  type = string
  default = "flask-app"
}
variable "health_check_path" {
  description = "Http path for task health check"
  default     = "/health"
}
