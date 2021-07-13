## Installation

```bash
git clone
make all
./cli mlflow
```

## Project

```bash
poetry shell
dvc init
COPY Batch_Files/*.csv Prediction_Batch_files/*.csv
dvc add data/Training_Batch_Files/*.csv data/Prediction_Batch_files/*.csv  # TODO data/.gitignore

# https://medium.com/analytics-vidhya/versioning-data-and-models-in-ml-projects-using-dvc-and-aws-s3-286e664a7209
vim .dvc/config  # replace AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY
dvc push
```

### note:

```bash
# instead of 
vim .dvc/config

# we can do:
dvc remote add -d myremote s3://mlflowtestmatt
dvc remote modify myremote access_key_id AWS_ACCESS_KEY_ID
dvc remote modify myremote secret_access_key AWS_SECRET_ACCESS_KEY
```

```bash
dvc run -n prepare -p prepare.categories -d src/prepare.py -o data/prepared python src/prepare.py
```
