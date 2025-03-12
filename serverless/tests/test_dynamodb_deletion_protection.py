import unittest
from checkov.common.models.enums import CheckResult
from ..dynamodb_deletion_protection import DynamoDBDeletionProtection

class TestDynamoDBDeletionProtection(unittest.TestCase):
    def setUp(self):
        self.checker = DynamoDBDeletionProtection()

    def test_table_with_proper_protection(self):
        conf = {
            'Type': 'AWS::DynamoDB::Table',
            'DeletionPolicy': 'Retain',
            'UpdateReplacePolicy': 'Retain',
            'Properties': {
                'TableName': 'GoodTable'
            }
        }
        
        result = self.checker.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.PASSED)

    def test_table_without_protection(self):
        conf = {
            'Type': 'AWS::DynamoDB::Table',
            'Properties': {
                'TableName': 'BadTable'
            }
        }
        
        result = self.checker.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.FAILED)

    def test_table_with_partial_protection(self):
        conf = {
            'Type': 'AWS::DynamoDB::Table',
            'DeletionPolicy': 'Retain',
            'Properties': {
                'TableName': 'PartiallyProtectedTable'
            }
        }
        
        result = self.checker.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.FAILED)

    def test_non_dynamodb_resource(self):
        conf = {
            'Type': 'AWS::S3::Bucket',
            'Properties': {
                'BucketName': 'TestBucket'
            }
        }
        
        result = self.checker.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.UNKNOWN)

if __name__ == '__main__':
    unittest.main()