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
        print(f"Scanning resource: {conf}")  # Debug print
        deletion_policy = conf.get('DeletionPolicy')
        update_policy = conf.get('UpdateReplacePolicy')
        
        if deletion_policy == 'Retain' and update_policy == 'Retain':
            return CheckResult.PASSED
        
        if deletion_policy != 'Retain':
            self.failure_reason = "DeletionPolicy should be set to 'Retain'"
            return CheckResult.FAILED
        
        if update_policy != 'Retain':
            self.failure_reason = "UpdateReplacePolicy should be set to 'Retain'"
            return CheckResult.FAILED
            
        return CheckResult.UNKNOWN

check = DynamoDBDeletionProtection()