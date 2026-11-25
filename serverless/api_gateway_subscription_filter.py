from functools import lru_cache

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.serverless.parsers.parser import parse


@lru_cache(maxsize=None)
def _template_resources(file_path):
    """Return the CloudFormation resources declared in a serverless file, keyed by logical ID.

    Parsed once per file, as a template usually has several subscription filters.
    """
    try:
        parsed = parse(file_path)
    except Exception:
        return {}
    if not parsed:
        return {}
    resources = (parsed[0].get('resources') or {}).get('Resources')
    return resources if isinstance(resources, dict) else {}


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

    def _as_string(self, value):
        """Return the string a property resolves to, or None when it can't be read statically.

        Plain strings (including unresolved serverless `${...}` variables) are returned as is,
        and `!Sub` templates are returned as their template string. Other intrinsic functions
        return None.
        """
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and 'Fn::Sub' in value:
            template = value['Fn::Sub']
            if isinstance(template, list) and template:
                template = template[0]
            if isinstance(template, str):
                return template
        return None

    def _resolve_log_group_name(self, conf, value):
        """Return the log group name, following a `!Ref` to an `AWS::Logs::LogGroup` in the same file.

        checkov records the source file on each resource as `__file__`, so the referenced
        log group can be looked up there. Returns None when the name can't be determined,
        e.g. the referenced log group has no explicit `LogGroupName`.
        """
        if isinstance(value, dict) and 'Ref' in value:
            logical_id = value['Ref']
            file_path = conf.get('__file__') or conf.get('Properties', {}).get('__file__')
            if not isinstance(logical_id, str) or not isinstance(file_path, str):
                return None
            log_group = _template_resources(file_path).get(logical_id)
            if not isinstance(log_group, dict) or log_group.get('Type') != 'AWS::Logs::LogGroup':
                return None
            return self._as_string(self._get_property(log_group, 'LogGroupName'))
        return self._as_string(value)

    def _is_api_gateway_log_group(self, log_group_name):
        """Check if this SubscriptionFilter is for an API Gateway log group."""
        if log_group_name is None:
            return False
        # Match both HTTP API and REST API log group patterns
        return log_group_name.startswith('/aws/http-api/') or log_group_name.startswith('/aws/api-gateway/')

    def scan_resource_conf(self, conf):
        # A `!Ref` is followed to the log group it points at. A LogGroupName that still
        # can't be resolved is treated as not being an API Gateway log group.
        log_group_name = self._resolve_log_group_name(conf, self._get_property(conf, 'LogGroupName'))

        # Only check SubscriptionFilters for API Gateway log groups
        if not self._is_api_gateway_log_group(log_group_name):
            return CheckResult.UNKNOWN

        # Check FilterName starts with S3-api-gateway-logs-
        filter_name = self._as_string(self._get_property(conf, 'FilterName'))
        if not filter_name or not filter_name.startswith('S3-api-gateway-logs-'):
            self.failure_reason = "FilterName should start with 'S3-api-gateway-logs-'"
            return CheckResult.FAILED
        
        # Check DestinationArn points to Firehose. Compared case-insensitively as
        # serverless `${param:...}` variables are not resolved by checkov and are
        # left as literal strings (e.g. '${param:apiLogsFirehoseStreamArn}').
        destination_arn = self._get_property(conf, 'DestinationArn')
        if not destination_arn or 'apilogsfirehosestreamarn' not in str(destination_arn).lower():
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

