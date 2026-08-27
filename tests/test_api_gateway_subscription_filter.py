import pytest
from checkov.common.models.enums import CheckResult
from serverless.api_gateway_subscription_filter import ApiGatewaySubscriptionFilter


@pytest.fixture
def checker():
    return ApiGatewaySubscriptionFilter()


# --- PASSING CASES ---

def test_valid_http_api_subscription_filter(checker):
    """A correctly configured HTTP API subscription filter should pass."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'FilterPattern': '',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED


def test_valid_rest_api_subscription_filter(checker):
    """A correctly configured REST API subscription filter should pass."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/api-gateway/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'FilterPattern': '',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED


def test_valid_subscription_filter_with_unresolved_param_variable(checker):
    """DestinationArn using an unresolved `${param:...}` serverless variable
    (checkov does not resolve `param:` references) should still pass, matched
    case-insensitively against the expected firehose stream reference."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/api-gateway/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'FilterPattern': '',
            'DestinationArn': '${param:apiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED


def test_properties_at_root_level(checker):
    """Properties at root level (not nested) should also be checked."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'LogGroupName': '/aws/http-api/my-service-prod',
        'FilterName': 'S3-api-gateway-logs-my-service-prod',
        'FilterPattern': '',
        'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
        'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
        'Distribution': 'Random'
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED


# --- UNKNOWN CASES (non-API Gateway log groups) ---

def test_non_api_gateway_log_group_returns_unknown(checker):
    """SubscriptionFilters for non-API Gateway log groups should return UNKNOWN."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/lambda/my-function',
            'FilterName': 'some-other-filter',
            'DestinationArn': 'some-other-arn',
            'RoleArn': 'some-role'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.UNKNOWN


def test_missing_log_group_name_returns_unknown(checker):
    """SubscriptionFilters without LogGroupName should return UNKNOWN."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.UNKNOWN


# --- FAILING CASES ---

def test_missing_filter_name(checker):
    """Missing FilterName should fail."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "FilterName should start with 'S3-api-gateway-logs-'" in checker.failure_reason


def test_wrong_filter_name_prefix(checker):
    """FilterName not starting with S3-api-gateway-logs- should fail."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': 'wrong-prefix-my-service-prod',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "FilterName should start with 'S3-api-gateway-logs-'" in checker.failure_reason


def test_missing_destination_arn(checker):
    """Missing DestinationArn should fail."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "DestinationArn should reference ApiLogsFirehoseStreamArn" in checker.failure_reason


def test_wrong_destination_arn(checker):
    """DestinationArn not referencing ApiLogsFirehoseStreamArn should fail."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'DestinationArn': 'arn:aws:firehose:eu-west-1:123456789:deliverystream/wrong-stream',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "DestinationArn should reference ApiLogsFirehoseStreamArn" in checker.failure_reason


def test_missing_role_arn(checker):
    """Missing RoleArn should fail."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "RoleArn must be set" in checker.failure_reason


def test_missing_distribution(checker):
    """Missing Distribution should fail."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "Distribution should be set to 'Random'" in checker.failure_reason


def test_wrong_distribution_value(checker):
    """Distribution not set to Random should fail."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': 'S3-api-gateway-logs-my-service-prod',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'ByLogStream'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "Distribution should be set to 'Random'" in checker.failure_reason

