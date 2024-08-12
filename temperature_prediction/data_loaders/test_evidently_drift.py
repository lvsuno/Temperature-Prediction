# if 'data_loader' not in globals():
#     from mage_ai.data_preparation.decorators import data_loader
# if 'test' not in globals():
#     from mage_ai.data_preparation.decorators import test

# import json


# @data_loader
# def load_data(*args, **kwargs):
#     """
#     Template code for loading data from any source.

#     Returns:
#         Anything (e.g. data frame, dictionary, array, int, str, etc.)
#     """
#     # Opening JSON file
#     f = open('data/result.json')

#     # returns JSON object as
#     # a dictionary
#     result = json.load(f)
#     target_drift = result['metrics'][0]['result']['drift_score']
#     print(target_drift)
#     num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
#     print(num_drifted_columns)
#     return result


# @test
# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'
