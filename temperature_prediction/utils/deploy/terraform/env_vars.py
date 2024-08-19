import os
import json
from typing import Optional

from temperature_prediction.utils.deploy.terraform.constants import (
    ENV_VARS_KEY,
    TERRAFORM_AWS_FULL_PATH,
)
from temperature_prediction.utils.deploy.terraform.variables import update_variables
from temperature_prediction.utils.deploy.terraform.main_variables import update_main_tf


def update_json_file(file_path, new_variables):
    """Update a JSON file with new variables, ensuring uniqueness by "name" key.

    Args:
        file_path (str): The path to the JSON file to update.
        new_variables (list): A list of dictionaries representing new variables to add.
    """

    # Read the current content of the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Convert list of dicts to dict for easy name-based lookup
    data_dict = {item['name']: item for item in data}

    # Append new variables to the current data if they do not exist
    for new_var in new_variables:
        if new_var['name'] not in data_dict:
            data_dict[new_var['name']] = new_var

    # Convert dict back to list
    updated_data = list(data_dict.values())

    # Write the updated list back to the file
    with open(file_path, 'w') as file:
        json.dump(updated_data, file, indent=2)

    print(f'JSON file at {file_path} has been updated.')


def set_environment_variables(
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    password: Optional[str] = None,
    username: Optional[str] = None,
    smtp_email: Optional[str] = None,
    smtp_password: Optional[str] = None,
    experiments_developer: Optional[str] = None,
    mlflow_tracking_server_host: Optional[str] = None,
    model_name: Optional[str] = None,
    default_experiment_name: Optional[str] = None,
    default_tracking_uri: Optional[str] = None,
    default_artifact_initial_path: Optional[str] = None,
    default_artifact_root: Optional[str] = None,
) -> None:
    os.environ['TF_VAR_database_password'] = password or 'password'
    os.environ['TF_VAR_database_user'] = username or 'postgres'

    variables = {}
    variables_main_tf = {}
    env_vars_to_add = []

    if aws_access_key_id:
        os.environ['TF_VAR_aws_access_key_id'] = aws_access_key_id or ''
        variables['aws_access_key_id'] = '""'
        variables_main_tf['aws_access_key_id'] = 'var.aws_access_key_id'
        env_vars_to_add.append(
            {"name": 'AWS_ACCESS_KEY_ID', "value": '${aws_access_key_id}'}
        )

    if aws_access_key_id:
        os.environ['TF_VAR_aws_secret_access_key'] = aws_secret_access_key or ''
        variables['aws_secret_access_key'] = '""'
        variables_main_tf['aws_secret_access_key'] = 'var.aws_secret_access_key'
        env_vars_to_add.append(
            {"name": 'AWS_SECRET_ACCESS_KEY', "value": '${aws_secret_access_key}'}
        )

    if smtp_email:
        os.environ['TF_VAR_smtp_email'] = smtp_email or ''
        variables['smtp_email'] = '""'
        variables_main_tf['smtp_email'] = 'var.smtp_email'
        env_vars_to_add.append({"name": 'SMTP_EMAIL', "value": '${smtp_email}'})

    if smtp_password:
        os.environ['TF_VAR_smtp_password'] = smtp_password or ''
        variables['smtp_password'] = '""'
        variables_main_tf['smtp_password'] = 'var.smtp_password'
        env_vars_to_add.append({"name": 'SMTP_PASSWORD', "value": '${smtp_password}'})

    if experiments_developer:
        os.environ['TF_VAR_experiments_developer'] = experiments_developer or ''
        variables['experiments_developer'] = '""'
        variables_main_tf['experiments_developer'] = 'var.experiments_developer'
        env_vars_to_add.append(
            {"name": 'EXPERIMENTS_DEVELOPER', "value": '${experiments_developer}'}
        )

    if mlflow_tracking_server_host:
        os.environ['TF_VAR_mlflow_tracking_server_host'] = (
            mlflow_tracking_server_host or ''
        )
        variables['mlflow_tracking_server_host'] = '""'
        variables_main_tf['mlflow_tracking_server_host'] = (
            'var.mlflow_tracking_server_host'
        )
        env_vars_to_add.append(
            {
                "name": 'MLFLOW_TRACKING_SERVER_HOST',
                "value": '${mlflow_tracking_server_host}',
            }
        )

    if model_name:
        os.environ['TF_VAR_model_name'] = model_name or ''
        variables['model_name'] = '""'
        variables_main_tf['model_name'] = 'var.model_name'
        env_vars_to_add.append({"name": 'MODEL_NAME', "value": '${model_name}'})

    if default_experiment_name:
        os.environ['TF_VAR_default_experiment_name'] = default_experiment_name or ''
        variables['default_experiment_name'] = '""'
        variables_main_tf['default_experiment_name'] = 'var.default_experiment_name'
        env_vars_to_add.append(
            {"name": 'DEFAULT_EXPERIMENT_NAME', "value": '${default_experiment_name}'}
        )

    if default_tracking_uri:
        os.environ['TF_VAR_default_tracking_uri'] = default_tracking_uri or ''
        variables['default_tracking_uri'] = '""'
        variables_main_tf['default_tracking_uri'] = 'var.default_tracking_uri'
        env_vars_to_add.append(
            {"name": 'DEFAULT_TRACKING_URI', "value": '${default_tracking_uri}'}
        )

    if default_artifact_initial_path:
        os.environ['TF_VAR_default_artifact_initial_path'] = (
            default_artifact_initial_path or ''
        )
        variables['default_artifact_initial_path'] = '""'
        variables_main_tf['default_artifact_initial_path'] = (
            'var.default_artifact_initial_path'
        )
        env_vars_to_add.append(
            {
                "name": 'DEFAULT_ARTIFACT_INITIAL_PATH',
                "value": '${default_artifact_initial_path}',
            }
        )

    if default_artifact_root:
        os.environ['TF_VAR_default_artifact_root'] = default_artifact_root or ''
        variables['default_artifact_root'] = '""'
        variables_main_tf['default_artifact_root'] = 'var.default_artifact_root'
        env_vars_to_add.append(
            {"name": 'DEFAULT_ARTIFACT_ROOT', "value": '${default_artifact_root}'}
        )

    if variables:
        update_variables(variables)

    if variables_main_tf:
        update_main_tf(
            os.path.join(TERRAFORM_AWS_FULL_PATH, 'main.tf'),
            variables_main_tf,
        )

    if env_vars_to_add:
        update_json_file(
            os.path.join(TERRAFORM_AWS_FULL_PATH, f'{ENV_VARS_KEY}.json'),
            env_vars_to_add,
        )

    print(
        'Environment variables have been set/updated in env_vars.json, main.tf, and variables.tf'
    )
