import configparser
from os.path import expanduser

from pprint import pprint

USER_HOME = expanduser("~")

aws_profiles = {}
aws_credentials = {}


def load_aws_config():
    config = configparser.ConfigParser()
    config.read([f"{USER_HOME}/.aws/config"])
    for profile in config.sections():
        aws_profiles[profile] = {key: val for key, val in config[profile].items()}


def load_aws_credentials():
    config = configparser.ConfigParser()
    config.read([f"{USER_HOME}/.aws/credentials"])

load_aws_config()

pprint(aws_profiles)

