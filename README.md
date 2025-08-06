# yoto-checkov

A publicly available collection of checkov tests used for AWS and the Serverless framework.

## How To

### Get Set Up

```shell
# python version
brew install pyenv
pyenv install
pyenv local

# python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

### Upgrade Dependencies

```shell
pip install --upgrade -r requirements.txt
```

### Publish Changes

- Releases are done automatically using `semantic-release`
- Commits need to follow the [conventional commit specification](https://www.conventionalcommits.org/en/v1.0.0/#specification)
- Once pushed, semantic release versions releases using git tags

## Reference

### Structure

- The `./serverless` folder is used to store all serverless checks (used so consumer can load just the folders that want)
- Tests kept _outside_ of the `./serverless` folder otherwise `checkov` tries to read them (and errors as it doesn't know `pytest`)

### The Custom Checks

- `dynamodb_deletion_protection` - to ensure _all_ tables have deletion protection enabled (it needs to be explicitly set in serverless) after an incident where serverless deleted a table during deploy.
- `cloudwatch_log_retention` - to avoid storing logs forever (costs) and deletion requests periods (30 days to action a deletion request of all PII for a user). If logs were kept longer than 30 days would have to find and remove any logs associated to the deletion request which is difficult and time consuming.
