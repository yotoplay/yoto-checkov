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

def test_log_group_with_retention_less_than_30_days_in_root(checker):
    conf = {
        'Type': 'AWS::Logs::LogGroup',
        'RetentionInDays': limitInDays - 1
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED

def test_log_group_with_retention_less_than_30_days_in_properties(checker):
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
    assert checker.failure_reason.startswith("RetentionInDays should be set to 30 days or less")

def test_log_group_with_retention_greater_than_30_days_in_root(checker):
    conf = {
        'Type': 'AWS::Logs::LogGroup',
        'RetentionInDays': limitInDays + 1,
        'Properties': {
            'LogGroupName': 'BadRetentionLogGroup'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason.startswith("RetentionInDays should be set to 30 days or less")

def test_log_group_with_retention_greater_than_30_days_in_properties(checker):
    conf = {
        'Type': 'AWS::Logs::LogGroup',
        'Properties': {
            'LogGroupName': 'BadRetentionLogGroup',
            'RetentionInDays': limitInDays + 1
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason.startswith("RetentionInDays should be set to 30 days or less")