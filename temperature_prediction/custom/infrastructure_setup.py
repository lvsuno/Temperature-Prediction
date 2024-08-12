import os

from temperature_prediction.utils.deploy.terraform.setup import (
    setup_configurations,
    download_terraform_configurations,
)
from temperature_prediction.utils.deploy.terraform.env_vars import (
    set_environment_variables,
)

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def setup(*args, **kwargs):
    """
    Downloads the base configurations for Terraform maintained and provided by Mage
    https://github.com/mage-ai/mage-ai-terraform-templates

    1. Updates variables in the Terraform variables file.
    2. Adds variables into the main.tf template env_vars.
    3. Adds environment variables to env_vars.json.

    prevent_destroy_ecr:
        True
    project_name:
        "mlops"

    Use the current environment variables as the environment variables in production.
    Change this if you want different values.
    In a real world environment, we’d have different values but this is here for
    demonstration purposes and for convenience.

    """
    download_terraform_configurations()

    setup_configurations(
        prevent_destroy_ecr=kwargs.get('prevent_destroy_ecr'),
        project_name=kwargs.get('project_name', os.getenv('PROJECT_NAME_DEPLOYMENT')),
    )

    set_environment_variables(
        password=kwargs.get('password', os.getenv('POSTGRES_PASSWORD')),
        username=kwargs.get('username', os.getenv('POSTGRES_USER')),
        smtp_email=kwargs.get('smtp_email', os.getenv('SMTP_EMAIL')),
        smtp_password=kwargs.get('smtp_password', os.getenv('SMTP_PASSWORD')),
        experiments_developer=kwargs.get(
            'EXPERIMENTS_DEVELOPER', os.getenv('EXPERIMENTS_DEVELOPER')
        ),
        mlflow_tracking_server_host=kwargs.get(
            'MLFLOW_TRACKING_SERVER_HOST', os.getenv('MLFLOW_TRACKING_SERVER_HOST')
        ),
        model_name=kwargs.get('MODEL_NAME', os.getenv('MODEL_NAME')),
        default_experiment_name=kwargs.get(
            'DEFAULT_EXPERIMENT_NAME', os.getenv('DEFAULT_EXPERIMENT_NAME')
        ),
        default_tracking_uri=kwargs.get(
            'DEFAULT_TRACKING_URI', os.getenv('DEFAULT_TRACKING_URI')
        ),
        default_artifact_initial_path=kwargs.get(
            'DEFAULT_ARTIFACT_INITIAL_PATH', os.getenv('DEFAULT_ARTIFACT_INITIAL_PATH')
        ),
        default_artifact_root=kwargs.get(
            'DEFAULT_ARTIFACT_ROOT', os.getenv('DEFAULT_ARTIFACT_ROOT')
        ),
    )
