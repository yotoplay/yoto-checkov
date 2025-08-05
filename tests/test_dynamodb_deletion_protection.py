import pytest
from checkov.common.models.enums import CheckResult
from serverless.dynamodb_deletion_protection import DynamoDBDeletionProtection

@pytest.fixture
def checker():
    return DynamoDBDeletionProtection()

def test_table_with_proper_protection(checker):
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'DeletionPolicy': 'Retain',
        'UpdateReplacePolicy': 'Retain',
        'Properties': {
            'TableName': 'GoodTable'
        }
    }
    
    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED

def test_table_without_protection(checker):
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'Properties': {
            'TableName': 'NoProtectionTable'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "DeletionPolicy should be set to 'Retain'"

def test_table_with_wrong_deletion_policy(checker):
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'DeletionPolicy': 'Delete',
        'UpdateReplacePolicy': 'Retain',
        'Properties': {
            'TableName': 'BadDeletionTable'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "DeletionPolicy should be set to 'Retain'"

def test_table_with_wrong_update_policy(checker):
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'DeletionPolicy': 'Retain',
        'UpdateReplacePolicy': 'Delete',
        'Properties': {
            'TableName': 'BadUpdateTable'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "UpdateReplacePolicy should be set to 'Retain'"