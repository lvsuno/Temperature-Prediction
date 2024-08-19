"""
Test docker
"""

import requests
from deepdiff import DeepDiff

datetime_str = '2024-08-09 23:00:00'

data = {"Station ID": 50840, "Date/Time (LST)": datetime_str}

URL = 'http://localhost:9696/predict'

# URL = 'http://application-load-balancer-1406699668.us-east-1.elb.amazonaws.com/predict'

actual_response = requests.post(URL, json=data, timeout=30).json()

# print("actual response:")

# print(json.dumps(actual_response, indent=2))

expected_response = {'prediction': 14}

diff = DeepDiff(actual_response, expected_response, significant_digits=1)

print(f"diff={diff}")

assert "type_changes" not in diff
assert "values_changed" not in diff


print("Integration Test succeed")
