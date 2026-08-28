from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class DynamoDBDeletionProtection(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DynamoDB tables have deletion protection policies"
        id = "CKV_CUSTOM_DYNAMODB_DELETION_PROTECTION"
        supported_resources = ['AWS::DynamoDB::Table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def _is_retain_or_unresolved(self, policy):
        """Accept an explicit 'Retain', or an unresolved serverless variable
        (e.g. '${self:custom.deletionPolicy.${self:provider.stage}}') which
        checkov cannot statically resolve to a value per-stage."""
        if policy == 'Retain':
            return True
        return isinstance(policy, str) and policy.startswith('${') and policy.endswith('}')

    def scan_resource_conf(self, conf):
        deletion_protection_enabled = conf.get('Properties', {}).get('DeletionProtectionEnabled')
        if deletion_protection_enabled is not True:
            self.failure_reason = "Properties.DeletionProtectionEnabled should be set to true"
            return CheckResult.FAILED

        deletion_policy = conf.get('DeletionPolicy')
        if not self._is_retain_or_unresolved(deletion_policy):
            self.failure_reason = "DeletionPolicy should be set to 'Retain'"
            return CheckResult.FAILED

        update_policy = conf.get('UpdateReplacePolicy')
        if not self._is_retain_or_unresolved(update_policy):
            self.failure_reason = "UpdateReplacePolicy should be set to 'Retain'"
            return CheckResult.FAILED

        return CheckResult.PASSED

check = DynamoDBDeletionProtection()