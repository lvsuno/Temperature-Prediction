# Step to permanently delete a mlflow experiment

1. Delete simply the experiment. It will be marked as deleted in the artifacts storage postgres database.
```python
    import mlflow
    mlflow.set_tracking_uri(os.getenv('DEFAULT_TRACKING_URI'))
    _, id =setup_experiment()
    mlflow.delete_experiment(id)
```
2. Go to the s3 bucket and delete the folder containing the experiment storage

3. Even with step 1 and 2, they are data present in the postgres backend. We have to clean it so that we can run a fresh experiment
   + Connect to your EC2 server
   + Connect to your RDS database using this `psql -h mlflow-backend-db.c3omcoy2mwg1.us-east-1.rds.amazonaws.com -p 5432 -d  mlflow_db -U mlflow -W`. Make sure that you have installed psql before or use `sudo yum -y install postgresql15`. For more informations, readers can refer to this [link](https://stackoverflow.com/questions/72307187/how-to-install-postgresql-client-to-amazon-ec2-linux-machine)
   + After you have type your password, it will bring you to your database console. Run the following code to delete the data:
   ```sql
        DELETE FROM experiment_tags WHERE experiment_id=ANY(
        SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
        );
        DELETE FROM latest_metrics WHERE run_uuid=ANY(
            SELECT run_uuid FROM runs WHERE experiment_id=ANY(
                SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
            )
        );
        DELETE FROM metrics WHERE run_uuid=ANY(
            SELECT run_uuid FROM runs WHERE experiment_id=ANY(
                SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
            )
        );
        DELETE FROM tags WHERE run_uuid=ANY(
            SELECT run_uuid FROM runs WHERE experiment_id=ANY(
                SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
            )
        );
        DELETE FROM params WHERE run_uuid=ANY(
            SELECT run_uuid FROM runs where experiment_id=ANY(
                SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
        ));
        DELETE FROM runs WHERE experiment_id=ANY(
            SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
        );
        DELETE FROM experiments where lifecycle_stage='deleted';
   ```

   The psql command line [guide](https://tomcam.github.io/postgres/) can help you.