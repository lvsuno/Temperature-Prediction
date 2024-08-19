import os
from typing import Optional
from tempfile import TemporaryDirectory

from temperature_prediction.utils.deploy.github import git_clone, copy_files
from temperature_prediction.utils.deploy.terraform.env_vars import update_json_file
from temperature_prediction.utils.deploy.terraform.constants import (
    ENV_VARS_KEY,
    TERRAFORM_AWS_NAME,
    TERRAFORM_REPO_URL,
    TERRAFORM_AWS_FULL_PATH,
)
from temperature_prediction.utils.deploy.terraform.variables import update_variables


def download_terraform_configurations():
    with TemporaryDirectory() as tmp_dir:
        git_clone(TERRAFORM_REPO_URL, tmp_dir)

        copy_files(
            os.path.join(tmp_dir, TERRAFORM_AWS_NAME),
            TERRAFORM_AWS_FULL_PATH,
        )


def setup_configurations(
    prevent_destroy_ecr: Optional[bool] = None,
    project_name: Optional[str] = None,
):
    if project_name:
        project_name = f'"{project_name}"'
    else:
        project_name = '"temp-pred"'

    docker_image = '"mageai/mageai:alpha"'
    aws_region = '"us-east-1"'
    ecs_task_cpu = 4096
    availability_zones = [
        "us-east-1a",
        "us-east-1b",
        "us-east-1c",
        "us-east-1d",
        "us-east-1e",
        "us-east-1f",
    ]

    print('Updating variables in variables.tf')
    print(f'  "app_name"            = {project_name}')
    print(f'  "docker_image"        = {docker_image}')
    print('  "enable_ci_cd"        = true')
    print(f'  "aws_region"        = {aws_region}')
    print(f'  "ecs_task_cpu"      = {ecs_task_cpu}')
    print(f'  "availability_zones" = {availability_zones}')

    variables = {
        "app_name": project_name,
        "docker_image": docker_image,
        "enable_ci_cd": True,
        "aws_region": aws_region,
        "ecs_task_cpu": ecs_task_cpu,
        "availability_zones": availability_zones,
    }

    if prevent_destroy_ecr is not None:
        variables['prevent_destroy_ecr'] = prevent_destroy_ecr
        print(f'  "prevent_destroy_ecr" = {"true" if prevent_destroy_ecr else "false"}')

    update_variables(variables)

    update_json_file(
        os.path.join(TERRAFORM_AWS_FULL_PATH, f'{ENV_VARS_KEY}.json'),
        [
            {
                "name": 'MAGE_PRESENTERS_DIRECTORY',
                "value": 'temperature_prediction/presenters',
            }
        ],
    )
