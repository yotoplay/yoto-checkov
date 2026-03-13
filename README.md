# yoto-checkov

A publicly available collection of checkov tests used checking AWS resources created by Serverless. Used to extend the suite of checkov tests we run in CI as part of validating our cloud configuration.

## How To

### Consume A Specific Version

In your `checkov.yml` specify the git tag you want to run against:

```yaml
external-checks-git:
  - https://github.com/yotoplay/yoto-checkov.git//serverless?ref=<semver>
  - https://github.com/yotoplay/yoto-checkov.git//serverless?ref=v1.2.0
```

### Get Set Up

```shell
# python version
brew install pyenv
pyenv install
pyenv local

# python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

### Develop Checks Locally

1. Run the checks locally against another repo, like this:

```shell
checkov -d ../yoto-fulfillment-api --external-checks-dir ./serverless --framework serverless
```

2. Amend the serverless config in repo in question to prove your check fails
3. Remember to key aspects of checkov:
   - it interprets serverless.yml as Cloudformation resources (but does not actually generate Cloudformation)
   - it can only work at the resource level (i.e. functions). You cannot check anything at a global level (like under the `provider:` section)

### Upgrade Dependencies

```shell
pip install --upgrade -r requirements.txt
```

### Publish Changes

- Releases are done automatically using `semantic-release`
- Commits need to follow the [conventional commit specification](https://www.conventionalcommits.org/en/v1.0.0/#specification)
- Once pushed, semantic release versions releases using git tags

## Reference

### Limitations

- `checkov` scans the serverless.yml and builds an object tree for all the resources that the serverless.yml would create
- It is not able to look at global settings. For example `provider:logRetentionInDays` as 'provider' is not an AWS resource. Instead it will scan over all 'functions' defined in the serverless.yml. This means checking any global settings is not possible.

### Structure

- The `./serverless` folder is used to store all serverless checks (used so consumer can load just the folders that want)
- Tests kept _outside_ of the `./serverless` folder otherwise `checkov` tries to read them (and errors as it doesn't know `pytest`)

### The Custom Checks

- `CKV_CUSTOM_DYNAMODB_DELETION_PROTECTION` (`dynamodb_deletion_protection`) - to ensure _all_ tables have deletion protection enabled (it needs to be explicitly set in serverless) after an incident where serverless deleted a table during deploy.
- `CKV_CUSTOM_CLOUDWATCH_LOG_RETENTION` (`cloudwatch_log_retention`) - to avoid storing logs forever (costs) and deletion requests periods (30 days to action a deletion request of all PII for a user). If logs were kept longer than 30 days it would mean finding and removing any logs associated to the deletion request - which is difficult and time consuming.
