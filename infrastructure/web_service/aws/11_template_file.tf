data "template_file" "task_definition_template" {
  template = file("task_definition.json.tpl")
  vars = {
    REPOSITORY_URL = var.flask_app_image
    FLASK_APP = var.flask_app
    FLASK_ENV = var.flask_env
    FLASK_APP_HOME = var.flask_app_home
    FLASK_APP_PORT = var.flask_app_port
    AWS_ACCESS_KEY_ID=var.access_key
    AWS_SECRET_ACCESS_KEY=var.secret_key
    REGION = var.region
    CLOUDWATCH_GROUP = aws_cloudwatch_log_group.logs.name

  }
}
