from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ApiGatewaySubscriptionFilter(BaseResourceCheck):
    def __init__(self):
        name = "Ensure API Gateway log SubscriptionFilters are correctly configured for S3/Firehose export"
        id = "CKV_CUSTOM_API_GATEWAY_SUBSCRIPTION_FILTER"
        supported_resources = ['AWS::Logs::SubscriptionFilter']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def _get_property(self, conf, prop_name):
        """Get a property from either root level or nested Properties."""
        return conf.get(prop_name) or conf.get('Properties', {}).get(prop_name)

    def _is_api_gateway_log_group(self, log_group_name):
        """Check if this SubscriptionFilter is for an API Gateway log group."""
        if log_group_name is None:
            return False
        # Match both HTTP API and REST API log group patterns
        return log_group_name.startswith('/aws/http-api/') or log_group_name.startswith('/aws/api-gateway/')

    def scan_resource_conf(self, conf):
        log_group_name = self._get_property(conf, 'LogGroupName')
        
        # Only check SubscriptionFilters for API Gateway log groups
        if not self._is_api_gateway_log_group(log_group_name):
            return CheckResult.UNKNOWN
        
        # Check FilterName starts with S3-api-gateway-logs-
        filter_name = self._get_property(conf, 'FilterName')
        if not filter_name or not filter_name.startswith('S3-api-gateway-logs-'):
            self.failure_reason = "FilterName should start with 'S3-api-gateway-logs-'"
            return CheckResult.FAILED
        
        # Check DestinationArn points to Firehose
        destination_arn = self._get_property(conf, 'DestinationArn')
        if not destination_arn or 'ApiLogsFirehoseStreamArn' not in str(destination_arn):
            self.failure_reason = "DestinationArn should reference ApiLogsFirehoseStreamArn"
            return CheckResult.FAILED
        
        # Check RoleArn is set
        role_arn = self._get_property(conf, 'RoleArn')
        if not role_arn:
            self.failure_reason = "RoleArn must be set for the SubscriptionFilter"
            return CheckResult.FAILED
        
        # Check Distribution is Random
        distribution = self._get_property(conf, 'Distribution')
        if distribution != 'Random':
            self.failure_reason = "Distribution should be set to 'Random'"
            return CheckResult.FAILED
        
        return CheckResult.PASSED


check = ApiGatewaySubscriptionFilter()

