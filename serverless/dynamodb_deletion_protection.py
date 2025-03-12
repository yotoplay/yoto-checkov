from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class DynamoDBDeletionProtection(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DynamoDB tables have deletion protection policies"
        id = "CKV_CUSTOM_DYNAMODB_DELETION_PROTECTION"
        supported_resources = ['AWS::DynamoDB::Table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        print(f"Scanning resource: {conf}")
        
        if conf.get('Type') != 'AWS::DynamoDB::Table':
            return CheckResult.UNKNOWN
        
        has_deletion_policy = conf.get('DeletionPolicy') == 'Retain'
        has_update_policy = conf.get('UpdateReplacePolicy') == 'Retain'
        
        if has_deletion_policy and has_update_policy:
            return CheckResult.PASSED
        
        return CheckResult.FAILED

check = DynamoDBDeletionProtection()