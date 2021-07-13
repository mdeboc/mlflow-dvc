import os
import yaml
import argparse
import joblib
import mlflow
from mlflow.tracking import MlflowClient


def get_config(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)

    return config


def log_production_model(config):
    # read pipeline params
    mlflow_config = config["mlflow_config"]
    remote_server_uri = mlflow_config["remote_server_uri"]
    model_name = mlflow_config["registered_model_name"]

    mlflow.set_tracking_uri(remote_server_uri)

    runs = mlflow.search_runs(experiment_ids=1)
    lowest = runs["metrics.auc"].sort_values(ascending=False)[0]
    lowest_run_id = runs[runs["metrics.auc"] == lowest]["run_id"][0]

    client = MlflowClient()
    for mv in client.search_model_versions(f"name='{model_name}'"):
        mv = dict(mv)

        if mv["run_id"] == lowest_run_id:
            current_version = mv["version"]
            logged_model = mv["source"]
            client.transition_model_version_stage(
                name=model_name, version=current_version, stage="Production"
            )
        else:
            current_version = mv["version"]
            client.transition_model_version_stage(
                name=model_name, version=current_version, stage="Staging"
            )

    loaded_model = mlflow.pyfunc.load_model(logged_model)

    model_path = config["webapp_model_dir"]
    if not os.path.isfile(model_path):
        directory = os.path.dirname(model_path)
        os.makedirs(directory, exist_ok=True)

    joblib.dump(loaded_model, model_path)


def get_prod_model(config_path):
    config = get_config(config_path)
    log_production_model(config)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    get_prod_model(config_path=parsed_args.config)
