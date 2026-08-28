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
            'TableName': 'GoodTable',
            'DeletionProtectionEnabled': True
        }
    }
    
    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED

def test_table_with_unresolved_serverless_variable_policies(checker):
    """Serverless `${self:...}` variables that checkov can't resolve are left as
    literal strings. These should be tolerated rather than treated as failures,
    since the actual value may resolve to 'Retain' depending on stage."""
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'DeletionPolicy': '${self:custom.deletionPolicy.${self:provider.stage}}',
        'UpdateReplacePolicy': '${self:custom.deletionPolicy.${self:provider.stage}}',
        'Properties': {
            'TableName': 'GoodTable',
            'DeletionProtectionEnabled': True
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.PASSED

def test_table_without_deletion_protection_enabled(checker):
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'DeletionPolicy': 'Retain',
        'UpdateReplacePolicy': 'Retain',
        'Properties': {
            'TableName': 'NoProtectionTable'
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "Properties.DeletionProtectionEnabled should be set to true"

def test_table_with_deletion_protection_enabled_false(checker):
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'DeletionPolicy': 'Retain',
        'UpdateReplacePolicy': 'Retain',
        'Properties': {
            'TableName': 'NoProtectionTable',
            'DeletionProtectionEnabled': False
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "Properties.DeletionProtectionEnabled should be set to true"

def test_table_without_protection(checker):
    conf = {
        'Type': 'AWS::DynamoDB::Table',
        'Properties': {
            'TableName': 'NoProtectionTable',
            'DeletionProtectionEnabled': True
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
            'TableName': 'BadDeletionTable',
            'DeletionProtectionEnabled': True
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
            'TableName': 'BadUpdateTable',
            'DeletionProtectionEnabled': True
        }
    }

    result = checker.scan_resource_conf(conf)
    assert result == CheckResult.FAILED
    assert checker.failure_reason == "UpdateReplacePolicy should be set to 'Retain'"