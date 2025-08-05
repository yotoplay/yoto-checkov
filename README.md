# yoto-checkov

A publicly available collection of checkov tests used for AWS and the Serverless framework.

## Run tests

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Release

- Make your changes
- Commit using conventional commit messages
- Run the below command to create a new release (form a semver'd git tag)

```shell
semantic-release version --no-vcs-release
```
