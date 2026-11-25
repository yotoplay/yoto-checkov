"""End-to-end test: run checkov's serverless runner with this repo's checks, as consumers' CI does."""
import logging
from pathlib import Path

import pytest
from checkov.runner_filter import RunnerFilter
from checkov.serverless.runner import Runner

CHECK_ID = 'CKV_CUSTOM_API_GATEWAY_SUBSCRIPTION_FILTER'
REPO_ROOT = Path(__file__).parent.parent
FIXTURE_DIR = REPO_ROOT / 'tests' / 'fixtures' / 'subscription_filter'


@pytest.fixture(scope='module')
def scan():
    """Scan the fixture once, capturing errors checkov logs while running checks."""
    errors = []

    class ErrorCollector(logging.Handler):
        def emit(self, record):
            errors.append(record.getMessage())

    handler = ErrorCollector(level=logging.ERROR)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    try:
        report = Runner().run(
            root_folder=str(FIXTURE_DIR),
            external_checks_dir=[str(REPO_ROOT / 'serverless')],
            runner_filter=RunnerFilter(framework=['serverless'], checks=[CHECK_ID]),
        )
    finally:
        root_logger.removeHandler(handler)

    return report, errors


def resource_names(records):
    return {record.resource.split('.')[-1] for record in records if record.check_id == CHECK_ID}


def test_runs_without_errors(scan):
    """No resource makes the check error, including a `!Ref` to a non-API Gateway log group."""
    _, errors = scan
    assert [error for error in errors if CHECK_ID in error] == []


def test_passes_correctly_configured_filters(scan):
    """Correct filters pass, whether the log group is a literal name or a `!Ref`."""
    report, _ = scan
    assert resource_names(report.passed_checks) == {'PassesRefToHttpApiLogGroup', 'PassesLiteralHttpApiLogGroup'}


def test_fails_misconfigured_filter_on_ref_log_group(scan):
    """A misconfigured filter on a `!Ref`'d API Gateway log group fails rather than being skipped."""
    report, _ = scan
    assert resource_names(report.failed_checks) == {'FailsRefToRestApiLogGroupWithWrongFilterName'}
