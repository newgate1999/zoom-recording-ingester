import configparser
from os.path import expanduser
from os import getenv
import boto3
from pathlib import Path
from ssm_cache import SSMParameterGroup, SSMParameter, InvalidParameterError
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv

from pprint import pprint

VALID_PARAM_TYPES = ["String", "SecureString", "StringList"]
PROJECT = "zoom-ingester"

env_file = join(dirname(__file__), ".env")
load_dotenv(env_file)

# make sure we're using the same client as the SSMParameter objects
ssm = boto3.client('ssm')
SSMParameter.set_ssm_client(ssm)


def get_profiles():
    config = configparser.ConfigParser()
    user_home = expanduser("~")
    config.read([f"{user_home}/.aws/credentials"])
    return config.sections()


def get_stacks():
    ssm = boto3.client("ssm")
    r = ssm.get_parameters_by_path(
        Path=f"/{PROJECT}", Recursive=True, WithDecryption=False
    )

    names = [param["Name"] for param in r["Parameters"]]
    stacks = [name.split(f"/{PROJECT}/")[1] for name in names]

    return stacks


def current_stack():
    return os.getenv("CURRENT")


def select_stack():
    stacks = get_stacks()

    if not stacks:
        return None

    for num, stack in enumerate(stacks):
        print(f"{num + 1} {'*' if stack == current_stack() else ' '} {stack}")

    while True:
        num = input("\nStack number: ")

        if not num.isdigit() or int(num) == 0 or int(num) > len(stacks):
            print("\nEnter valid stage number.")
        else:
            stack = stacks[int(num) - 1]
            break
    return stack


def switch_to(stack_name):
    with open(env_file, "w") as f:
        f.write(f"CURRENT={stack_name}")


class StackConfig:

    def __init__(self, stack_name, create=False):
        if not stack_name:
            raise Exception("Missing stack name")
        self.stack_name = stack_name

    def create(self):
        if self.exists():
            raise Exception("Config already exists")
        ssm.put_parameter(
            Name=self.path,
            Description=f"Config for {self.stack_name} stack",
            Value=json.dumps({}),
            Type="SecureString"
        )

    def exists(self):
        try:
            ssm.get_parameter(Name=self.path)
            return True
        except ssm.exceptions.ParameterNotFound:
            return False

    def delete(self):
        ssm.delete_parameter(Name=self.path)

    def show(self):
        try:
            r = ssm.get_parameter(Name=self.path, WithDecryption=True)
        except ssm.exceptions.ParameterNotFound:
            raise Exception("Config doesn't exist")
        print(f"Name: {r['Parameter']['Name']}")
        print("Value:")
        print(r["Parameter"]["Value"])

    def edit(self):
        pass

    @property
    def path(self):
        return (Path("/") / PROJECT / self.stack_name).as_posix()


# print(get_profiles())
# print(get_stacks())

# # config = StackConfig("test")
# # config.view()
# # config.delete()

# print(current_stack())
# switch_to("test")
# print(current_stack())
