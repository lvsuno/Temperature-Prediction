import pytest
from mage_ai.data_preparation.repo_manager import get_repo_path
from mage_ai.data_preparation.models.pipeline import Pipeline


@pytest.fixture
def sample_pipeline():
    pipeline_path = get_repo_path('data_preparation')
    pipeline = Pipeline.get(pipeline_path)
    return pipeline


def test_pipeline_execution(sample_pipeline):
    # Execute the pipeline
    sample_pipeline.execute()

    # Assertions for pipeline outputs
    output_block = sample_pipeline.get_block('build_export')
    output_data = output_block.get_data()

    assert output_data is not None
    assert len(output_data) > 0
