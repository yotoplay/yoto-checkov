import pytest
from checkov.common.models.enums import CheckResult
from serverless.cloudwatch_log_retention import CloudWatchLogRetention

limitInDays = 30

@pytest.fixture
def checker():
    return CloudWatchLogRetention()

def test_log_group_with_retention_30_days(checker):
    conf = {
        'Type': 'AWS::Logs::LogGroup',
        'Properties': {
            'LogGroupName': 'GoodLogGroup',
            'RetentionInDays': limitInDays
        }
    }
    
    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED

def test_log_group_with_retention_less_than_30_days(checker):
    conf = {
        'Type': 'AWS::Logs::LogGroup',
        'Properties': {
            'LogGroupName': 'GoodLogGroup',
            'RetentionInDays': limitInDays - 1
        }
    }
    
    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED

def test_log_group_without_retention_policy(checker):
    conf = {
        'Type': 'AWS::Logs::LogGroup',
        'Properties': {
            'LogGroupName': 'NoRetentionLogGroup'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "RetentionInDays should be set to 30 days or less (to reduce cost, and avoid deletion request periods)"

def test_log_group_with_retention_greater_than_30_days(checker):
    conf = {
        'Type': 'AWS::Logs::LogGroup',
        'Properties': {
            'LogGroupName': 'BadRetentionLogGroup',
            'RetentionInDays': limitInDays + 1
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "RetentionInDays should be set to 30 days or less (to reduce cost, and avoid deletion request periods)"