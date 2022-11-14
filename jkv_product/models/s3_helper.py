import logging
import boto3
from botocore.exceptions import ClientError


_logger = logging.getLogger(__name__)

# According to http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-query-string-auth.html
MAX_SIGNED_EXPIRATION_TIME = 7 * 24 * 60 * 60
MIN_SIGNED_EXPIRATION_TIME = 1


class S3Helper(object):
    def __init__(self, env):
        self.env = env

        IrConfigParam = env['ir.config_parameter'].sudo()
        self.access_key = IrConfigParam.get_param('aws_access_key_id')
        self.secret_key = IrConfigParam.get_param('aws_secret_access_key')
        self.bucket_name = IrConfigParam.get_param('bucket_name')
        self.s3_client = None

    def init(self):
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
            return self.s3_client
        except ClientError as e:
            _logger.error('Error while initializing S3 Client: %s', str(e))
            return None

    def generate_presigned_url(self, method, params, expiration=None):
        """
        This method generate link that has the access privilege of the signer
        This link can then be used to access the resources from S3 without signing in
        The generation is done without the need for connection to S3
        """
        s3_client = self.s3_client if self.s3_client else self.init()
        expiration = expiration or MAX_SIGNED_EXPIRATION_TIME
        try:
            response = s3_client.generate_presigned_url(
                method,
                Params=params,
                ExpiresIn=max(int(min(expiration, MAX_SIGNED_EXPIRATION_TIME)), MIN_SIGNED_EXPIRATION_TIME)
            )
            url = str(response)
            return url
        except ClientError as e:
            _logger.error('Could not execute %s from S3 with params %s. Got this error: %s', method, params, str(e))
            return None

    def generate_presigned_get_object(self, key, expiration=None, download=None):
        params = {
            'Bucket': self.bucket_name,
            'Key': key,
        }
        if download and download.get('filename') and download.get('content_type'):
            params.update({
                'ResponseContentDisposition': 'attachment;filename={}'.format(download['filename']),
                'ResponseContentType': download['content_type'],
            })
        return self.generate_presigned_url('get_object', params, expiration)
