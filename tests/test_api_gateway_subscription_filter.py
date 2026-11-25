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



# --- INTRINSIC FUNCTION CASES ---

def write_serverless_file(tmp_path, log_group_name):
    """Write a serverless.yml declaring a log group, and return its path."""
    log_group_name_line = f"        LogGroupName: {log_group_name}\n" if log_group_name else ""
    serverless_file = tmp_path / 'serverless.yml'
    serverless_file.write_text(
        "service: my-service\n"
        "provider:\n"
        "  name: aws\n"
        "  stage: prod\n"
        "resources:\n"
        "  Resources:\n"
        "    ApiLogGroup:\n"
        "      Type: AWS::Logs::LogGroup\n"
        "      Properties:\n"
        f"{log_group_name_line}"
        "        RetentionInDays: 30\n"
    )
    return str(serverless_file)


def ref_subscription_filter(file_path, filter_name):
    return {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': {'Ref': 'ApiLogGroup'},
            'FilterName': filter_name,
            'FilterPattern': '',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        },
        '__file__': file_path
    }


def test_ref_to_api_gateway_log_group_is_checked(checker, tmp_path):
    """A `!Ref` to an API Gateway log group in the same file is followed and checked."""
    file_path = write_serverless_file(tmp_path, '/aws/http-api/${self:service}-${self:provider.stage}')

    result = checker.scan_resource_conf(ref_subscription_filter(file_path, 'S3-api-gateway-logs-my-service-prod'))
    assert result == CheckResult.PASSED


def test_ref_to_api_gateway_log_group_with_wrong_filter_name_fails(checker, tmp_path):
    """A misconfigured filter on a `!Ref`'d API Gateway log group fails rather than being skipped."""
    file_path = write_serverless_file(tmp_path, '/aws/api-gateway/my-service-prod')

    result = checker.scan_resource_conf(ref_subscription_filter(file_path, 'wrong-prefix-my-service-prod'))
    assert result == CheckResult.FAILED
    assert "FilterName should start with 'S3-api-gateway-logs-'" in checker.failure_reason


def test_ref_to_other_log_group_returns_unknown(checker, tmp_path):
    """A `!Ref` to a non-API Gateway log group returns UNKNOWN."""
    file_path = write_serverless_file(tmp_path, '/aws/opensearch/my-domain/search-slow-logs')

    result = checker.scan_resource_conf(ref_subscription_filter(file_path, 'anything'))
    assert result == CheckResult.UNKNOWN


def test_ref_to_log_group_without_name_returns_unknown(checker, tmp_path):
    """A `!Ref` to a log group with a generated name returns UNKNOWN, as the name isn't known."""
    file_path = write_serverless_file(tmp_path, None)

    result = checker.scan_resource_conf(ref_subscription_filter(file_path, 'anything'))
    assert result == CheckResult.UNKNOWN


def test_ref_to_missing_resource_returns_unknown(checker, tmp_path):
    """A `!Ref` to a logical ID that isn't a log group in the file returns UNKNOWN."""
    file_path = write_serverless_file(tmp_path, '/aws/http-api/my-service-prod')
    conf = ref_subscription_filter(file_path, 'S3-api-gateway-logs-my-service-prod')
    conf['Properties']['LogGroupName'] = {'Ref': 'SomethingElse'}

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.UNKNOWN


def test_ref_log_group_name_without_source_file_returns_unknown(checker):
    """A `!Ref` LogGroupName with no source file to look it up in returns UNKNOWN instead of crashing."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': {'Ref': 'SearchSlowLogGroup'},
            'FilterPattern': '',
            'DestinationArn': 'arn:aws:lambda:eu-west-2:123456789012:function:datadog-forwarder'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.UNKNOWN


def test_sub_log_group_name_for_api_gateway_is_checked(checker):
    """A `!Sub` LogGroupName for an API Gateway log group is checked like a plain string."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': {'Fn::Sub': '/aws/http-api/my-service-${AWS::Region}'},
            'FilterName': {'Fn::Sub': 'S3-api-gateway-logs-my-service-${AWS::Region}'},
            'FilterPattern': '',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED


def test_sub_list_log_group_name_for_api_gateway_is_checked(checker):
    """The list form of `!Sub` is checked using its template string."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': {'Fn::Sub': ['/aws/api-gateway/${Name}', {'Name': 'my-service'}]},
            'FilterName': 'wrong-prefix-my-service-prod',
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "FilterName should start with 'S3-api-gateway-logs-'" in checker.failure_reason


def test_unresolvable_filter_name_fails(checker):
    """A FilterName built with an intrinsic that can't be resolved fails instead of crashing."""
    conf = {
        'Type': 'AWS::Logs::SubscriptionFilter',
        'Properties': {
            'LogGroupName': '/aws/http-api/my-service-prod',
            'FilterName': {'Fn::Join': ['-', ['S3-api-gateway-logs', 'my-service']]},
            'DestinationArn': '${cf:YotoInfrastructureKinesis-prod.ApiLogsFirehoseStreamArn}',
            'RoleArn': '!GetAtt CloudWatchLogsToFirehoseRole.Arn',
            'Distribution': 'Random'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert "FilterName should start with 'S3-api-gateway-logs-'" in checker.failure_reason
