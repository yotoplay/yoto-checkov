# yoto-checkov

A publicly available collection of checkov tests used for AWS and the Serverless framework.

## Run tests

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Upgrade Dependencies

```shell
pip install --upgrade -r requirements.txt
```

## Release

- Releases are done automatically using `semantic-release`
- Commits need to follow the [conventional commit specification](https://www.conventionalcommits.org/en/v1.0.0/#specification)
- Once pushed, semantic release versions releases using git tags
