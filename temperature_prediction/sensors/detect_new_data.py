import os

import pandas as pd
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric

if 'sensor' not in globals():
    from mage_ai.data_preparation.decorators import sensor


STATIONS_FOLDER = 'data/stations/'
OLD_TRAINING_FOLDER = 'data/Training/old/'
NEW_DATA_FOLDER = 'data/Training/new/'

target = "Temp (°C)"
num_features = ['Date_Time_Num']
cat_features = ['Station ID']

column_mapping = ColumnMapping(
    prediction=None,
    numerical_features=num_features,
    categorical_features=cat_features,
    target=target,
)

report = Report(
    metrics=[
        ColumnDriftMetric(column_name=target),
        DatasetDriftMetric(),  # ,
        #    DatasetMissingValuesMetric()
    ]
)


@sensor
def check_for_new_data(*args, **kwargs) -> bool:
    """
    Template code for checking if block or pipeline run completed.
    """

    if os.path.isfile(f'{NEW_DATA_FOLDER}X_train.csv'):

        reference_data_train_x = pd.read_csv(f'{OLD_TRAINING_FOLDER}X_train.csv')
        reference_data_val_x = pd.read_csv(f'{OLD_TRAINING_FOLDER}X_val.csv')
        reference_data_train_y = pd.read_csv(f'{OLD_TRAINING_FOLDER}y_train.csv')
        reference_data_val_y = pd.read_csv(f'{OLD_TRAINING_FOLDER}y_val.csv')

        reference_data_train = pd.concat(
            [reference_data_train_x, reference_data_train_y], axis=1
        )
        reference_data_val = pd.concat(
            [reference_data_val_x, reference_data_val_y], axis=1
        )

        reference_data = pd.concat(
            [reference_data_train, reference_data_val], ignore_index=True
        )

        current_data_train_x = pd.read_csv(f'{NEW_DATA_FOLDER}X_train.csv')
        current_data_val_x = pd.read_csv(f'{NEW_DATA_FOLDER}X_val.csv')
        current_data_train_y = pd.read_csv(f'{NEW_DATA_FOLDER}y_train.csv')
        current_data_val_y = pd.read_csv(f'{NEW_DATA_FOLDER}y_val.csv')

        current_data_train = pd.concat(
            [current_data_train_x, current_data_train_y], axis=1
        )
        current_data_val = pd.concat([current_data_val_x, current_data_val_y], axis=1)

        current_data = pd.concat(
            [current_data_train, current_data_val], ignore_index=True
        )

        report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=column_mapping,
        )

        result = report.as_dict()

        # # print(result)

        target_drift = result['metrics'][0]['result']['drift_detected']
        dataset_drift = result['metrics'][1]['result']['dataset_drift']
        all_data_train_x = pd.concat(
            [reference_data_train_x, current_data_train_x], ignore_index=True
        )
        all_data_train_y = pd.concat(
            [reference_data_train_y, current_data_train_y], ignore_index=True
        )
        all_data_val_x = pd.concat(
            [reference_data_val_x, current_data_val_x], ignore_index=True
        )
        all_data_val_y = pd.concat(
            [reference_data_val_y, current_data_val_y], ignore_index=True
        )

        all_data_train_x.to_csv(f'{OLD_TRAINING_FOLDER}X_train.csv', index=False)
        all_data_train_y.to_csv(f'{OLD_TRAINING_FOLDER}y_train.csv', index=False)
        all_data_val_x.to_csv(f'{OLD_TRAINING_FOLDER}X_val.csv', index=False)
        all_data_val_y.to_csv(f'{OLD_TRAINING_FOLDER}y_val.csv', index=False)

        os.remove(f'{NEW_DATA_FOLDER}X_train.csv')
        os.remove(f'{NEW_DATA_FOLDER}X_val.csv')
        os.remove(f'{NEW_DATA_FOLDER}y_train.csv')
        os.remove(f'{NEW_DATA_FOLDER}y_val.csv')

    if target_drift:
        should_train = True
        print('Retraining models...')
    elif dataset_drift:
        should_train = True
        print('Retraining models...')
    else:
        should_train = False
        print('Not enough drifts to retrain models.')

    return should_train
