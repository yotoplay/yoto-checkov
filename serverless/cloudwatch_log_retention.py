from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class CloudWatchLogRetention(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CloudWatch logs are retained for 30 days or less (to comply with deletion request periods)"
        id = "CKV_CUSTOM_CLOUDWATCH_LOG_RETENTION"
        supported_resources = ['AWS::Logs::LogGroup']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Check if RetentionInDays is at the root level
        retention_in_days = conf.get('RetentionInDays')
        
        # If not at root, check in Properties
        if retention_in_days is None and 'Properties' in conf:
            retention_in_days = conf['Properties'].get('RetentionInDays')
        
        if retention_in_days is None:
            self.failure_reason = "RetentionInDays should be set to 30 days or less"
            return CheckResult.FAILED
        
        if retention_in_days <= 30:
            return CheckResult.PASSED
        
        self.failure_reason = "RetentionInDays should be set to 30 days or less"
        return CheckResult.FAILED

check = CloudWatchLogRetention()