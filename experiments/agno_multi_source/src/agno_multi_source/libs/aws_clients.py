"""
AWS Service Clients for Multi-Source RAG System

This module provides centralized AWS service client management with proper configuration
and connection handling for S3, DynamoDB, Athena, and other AWS services.
"""

import logging
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import get_config

logger = logging.getLogger(__name__)


class AWSClients:
    """
    Centralized AWS service client manager.
    
    Provides singleton access to AWS services with proper configuration
    and error handling.
    """
    
    def __init__(self):
        self.config = get_config()
        self._s3_client = None
        self._dynamodb_client = None
        self._dynamodb_resource = None
        self._athena_client = None
        self._lambda_client = None
        self._session = None
    
    @property
    def session(self) -> boto3.Session:
        """Get or create a boto3 session"""
        if self._session is None:
            try:
                self._session = boto3.Session(
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_secret_access_key=self.config.aws_secret_access_key,
                    region_name=self.config.aws_region
                )
                logger.info(f"Created AWS session for region: {self.config.aws_region}")
            except Exception as e:
                logger.error(f"Failed to create AWS session: {e}")
                # Fallback to default credentials
                self._session = boto3.Session()
        
        return self._session
    
    @property
    def s3(self) -> boto3.client:
        """Get or create S3 client"""
        if self._s3_client is None:
            try:
                self._s3_client = self.session.client('s3')
                logger.debug("Created S3 client")
            except Exception as e:
                logger.error(f"Failed to create S3 client: {e}")
                raise
        
        return self._s3_client
    
    @property
    def dynamodb_client(self) -> boto3.client:
        """Get or create DynamoDB client"""
        if self._dynamodb_client is None:
            try:
                self._dynamodb_client = self.session.client('dynamodb')
                logger.debug("Created DynamoDB client")
            except Exception as e:
                logger.error(f"Failed to create DynamoDB client: {e}")
                raise
        
        return self._dynamodb_client
    
    @property
    def dynamodb_resource(self) -> boto3.resource:
        """Get or create DynamoDB resource"""
        if self._dynamodb_resource is None:
            try:
                self._dynamodb_resource = self.session.resource('dynamodb')
                logger.debug("Created DynamoDB resource")
            except Exception as e:
                logger.error(f"Failed to create DynamoDB resource: {e}")
                raise
        
        return self._dynamodb_resource
    
    @property
    def athena(self) -> boto3.client:
        """Get or create Athena client"""
        if self._athena_client is None:
            try:
                self._athena_client = self.session.client('athena')
                logger.debug("Created Athena client")
            except Exception as e:
                logger.error(f"Failed to create Athena client: {e}")
                raise
        
        return self._athena_client
    
    @property
    def lambda_client(self) -> boto3.client:
        """Get or create Lambda client"""
        if self._lambda_client is None:
            try:
                self._lambda_client = self.session.client('lambda')
                logger.debug("Created Lambda client")
            except Exception as e:
                logger.error(f"Failed to create Lambda client: {e}")
                raise
        
        return self._lambda_client
    
    def get_dynamodb_table(self, table_name: Optional[str] = None):
        """Get a DynamoDB table resource"""
        table_name = table_name or self.config.table_name
        if not table_name:
            raise ValueError("No table name provided and TABLE_NAME not configured")
        
        try:
            table = self.dynamodb_resource.Table(table_name)
            # Verify table exists by loading its metadata
            table.load()
            logger.debug(f"Connected to DynamoDB table: {table_name}")
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.error(f"DynamoDB table {table_name} not found")
                raise
            else:
                logger.error(f"Error accessing DynamoDB table {table_name}: {e}")
                raise
    
    def test_s3_connection(self) -> bool:
        """Test S3 connection by listing buckets"""
        try:
            self.s3.list_buckets()
            logger.info("S3 connection test successful")
            return True
        except Exception as e:
            logger.error(f"S3 connection test failed: {e}")
            return False
    
    def test_athena_connection(self) -> bool:
        """Test Athena connection by checking service status"""
        try:
            # Try to list query executions (should not fail if service is accessible)
            self.athena.list_query_executions(MaxResults=1)
            logger.info("Athena connection test successful")
            return True
        except Exception as e:
            logger.error(f"Athena connection test failed: {e}")
            return False
    
    def test_dynamodb_connection(self, table_name: Optional[str] = None) -> bool:
        """Test DynamoDB connection by checking table access"""
        try:
            table = self.get_dynamodb_table(table_name)
            # Try to scan with limit 1 to verify access
            table.scan(Limit=1)
            logger.info(f"DynamoDB connection test successful for table: {table.name}")
            return True
        except Exception as e:
            logger.error(f"DynamoDB connection test failed: {e}")
            return False
    
    def get_s3_object(self, bucket: str, key: str) -> dict:
        """Get an object from S3 with error handling"""
        try:
            response = self.s3.get_object(Bucket=bucket, Key=key)
            logger.debug(f"Retrieved S3 object: s3://{bucket}/{key}")
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"S3 object not found: s3://{bucket}/{key}")
                raise FileNotFoundError(f"S3 object not found: s3://{bucket}/{key}")
            else:
                logger.error(f"Error retrieving S3 object s3://{bucket}/{key}: {e}")
                raise
    
    def start_athena_query(self, query: str, database: str, output_location: str) -> Optional[str]:
        """Start an Athena query execution"""
        try:
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': database},
                ResultConfiguration={'OutputLocation': output_location}
            )
            query_execution_id = response['QueryExecutionId']
            logger.info(f"Started Athena query: {query_execution_id}")
            return query_execution_id
        except Exception as e:
            logger.error(f"Failed to start Athena query: {e}")
            return None
    
    def get_athena_query_status(self, query_execution_id: str) -> Optional[str]:
        """Get the status of an Athena query execution"""
        try:
            response = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
            status = response['QueryExecution']['Status']['State']
            logger.debug(f"Athena query {query_execution_id} status: {status}")
            return status
        except Exception as e:
            logger.error(f"Failed to get Athena query status for {query_execution_id}: {e}")
            return None
    
    def get_athena_query_results(self, query_execution_id: str) -> Optional[dict]:
        """Get the results of an Athena query execution"""
        try:
            response = self.athena.get_query_results(QueryExecutionId=query_execution_id)
            logger.debug(f"Retrieved Athena query results for: {query_execution_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get Athena query results for {query_execution_id}: {e}")
            return None
    
    def validate_configuration(self) -> bool:
        """Validate AWS configuration and connectivity"""
        if not self.config.is_aws_configured():
            logger.error("AWS credentials not configured")
            return False
        
        # Test connections
        tests = [
            ("S3", self.test_s3_connection),
            ("Athena", self.test_athena_connection),
        ]
        
        # Only test DynamoDB if table name is configured
        if self.config.table_name:
            tests.append(("DynamoDB", self.test_dynamodb_connection))
        
        all_passed = True
        for service, test_func in tests:
            try:
                if not test_func():
                    logger.error(f"{service} connection test failed")
                    all_passed = False
                else:
                    logger.info(f"{service} connection test passed")
            except Exception as e:
                logger.error(f"{service} connection test error: {e}")
                all_passed = False
        
        return all_passed


# Global singleton instance
_aws_clients_instance: Optional[AWSClients] = None


def get_aws_clients() -> AWSClients:
    """Get or create the global AWS clients singleton"""
    global _aws_clients_instance
    if _aws_clients_instance is None:
        _aws_clients_instance = AWSClients()
    return _aws_clients_instance 