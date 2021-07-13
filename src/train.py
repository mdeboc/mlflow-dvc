import sys
import os
import yaml
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import precision_recall_curve, roc_auc_score
import pickle
import argparse
from urllib.parse import urlparse
import mlflow
import mlflow.sklearn


def get_config(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)

    return config


def get_preprocessed_data(config, split):
    features_path = config["prepare"]["data_preprocessed"]

    # load the train features
    features_train_pkl = os.path.join(features_path, f"{split}.pkl")
    with open(features_train_pkl, "rb") as f:
        train_data = pickle.load(f)

    X = train_data.iloc[:, :-1]
    y = train_data.iloc[:, -1]

    return X, y


def get_best_f1(precisions, recalls):
    best_f1 = 0
    best_precision, best_recall = 0, 0
    for precision, recall in zip(precisions, recalls):
        f1 = 2 * (precision * recall) / (precision + recall)
        if f1 > best_f1:
            best_precision, best_recall = precision, recall
    return best_precision, best_recall


def train_and_predict(config):
    # read pipeline params
    alpha = config["train"]["alpha"]
    mlflow_config = config["mlflow_config"]
    remote_server_uri = mlflow_config["remote_server_uri"]

    mlflow.set_tracking_uri(remote_server_uri)
    mlflow.set_experiment(mlflow_config["experiment_name"])

    X_train, y_train = get_preprocessed_data(config, "train")
    X_test, y_test = get_preprocessed_data(config, "test")

    with mlflow.start_run(run_name=mlflow_config["run_name"]):
        # train the model
        clf = MultinomialNB(alpha=alpha)
        clf.fit(X_train, y_train)

        pred = clf.predict_proba(X_test)[:, 1]

        mlflow.log_param("alpha", alpha)

        precisions, recalls, thresholds = precision_recall_curve(y_test, pred)
        precision, recall = get_best_f1(precisions, recalls)
        auc = roc_auc_score(y_test, pred)

        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("auc", auc)

        tracking_url_type_store = urlparse(mlflow.get_artifact_uri()).scheme

        if tracking_url_type_store != "file":
            mlflow.sklearn.log_model(
                clf,
                "model",
                registered_model_name=mlflow_config["registered_model_name"],
            )
        else:
            mlflow.sklearn.load_model(clf, "model")

    return clf


def do_train(config_path):
    config = get_config(config_path)
    clf = train_and_predict(config)
    # save the model
    model_filename = config["train"]["outputed_model"]
    with open(model_filename, "wb") as f:
        pickle.dump(clf, f)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    do_train(config_path=parsed_args.config)
