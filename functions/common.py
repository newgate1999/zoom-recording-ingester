
import jwt
import time
import logging
import aws_lambda_logging
from functools import wraps
from os import getenv as env

ZOOM_API_KEY = env('ZOOM_API_KEY')
ZOOM_API_SECRET = env('ZOOM_API_SECRET')
LOG_LEVEL = env('DEBUG') and 'DEBUG' or 'INFO'
BOTO_LOG_LEVEL = env('BOTO_DEBUG') and 'DEBUG' or 'INFO'

def setup_logging(handler_func):

    @wraps(handler_func)
    def wrapped_func(event, context):

        extra_info = {'aws_request_id': context.aws_request_id}
        aws_lambda_logging.setup(
            level=LOG_LEVEL,
            boto_level=BOTO_LOG_LEVEL,
            **extra_info
        )

        logger = logging.getLogger()

        try:
            retval = handler_func(event, context)
        except Exception as e:
            logger.exception("handler failed!")
            raise

        return retval

    wrapped_func.__name__ = handler_func.__name__
    return wrapped_func


def gen_token(key=ZOOM_API_KEY, secret=ZOOM_API_SECRET, seconds_valid=60):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"iss": key, "exp": int(time.time() + seconds_valid)}
    return jwt.encode(payload, secret, headers=header)


