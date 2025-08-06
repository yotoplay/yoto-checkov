from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class CloudWatchLogRetention(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CloudWatch logs are retained for 30 days or less (to comply with deletion request periods, and reduce unnecessary costs)"
        id = "CKV_CUSTOM_CLOUDWATCH_LOG_RETENTION"
        supported_resources = ['AWS::Logs::LogGroup']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def _get_retention_days(self, conf):
        return conf.get('RetentionInDays') or conf.get('Properties', {}).get('RetentionInDays')

    def scan_resource_conf(self, conf):
        retention_in_days = self._get_retention_days(conf)
        
        if retention_in_days is None:
            self.failure_reason = "RetentionInDays should be set to 30 days or less"
            return CheckResult.FAILED
        
        if retention_in_days <= 30:
            return CheckResult.PASSED
        
        self.failure_reason = "RetentionInDays should be set to 30 days or less"
        return CheckResult.FAILED

check = CloudWatchLogRetention()