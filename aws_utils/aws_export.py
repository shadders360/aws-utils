"""Main module.
Assume a role and export AWS credentials.
"""
import boto3
import click
import configparser
import os
import questionary
import sys

from rich.console import Console
from rich.table import Table
from time import gmtime, strftime


class QuestionaryOption(click.Option):

    def __init__(self, param_decls=None, **attrs):
        click.Option.__init__(self, param_decls, **attrs)
        if not isinstance(self.type, click.Choice):
            raise Exception('ChoiceOption type arg must be click.Choice')

    def prompt_for_value(self, ctx):
        aws_config = AwsConfig()
        aws_config.to_console()
        val = questionary.select(
                self.prompt,
                choices=aws_config.get_profile_names(),
        ).ask()
        return val


# parse the config file
class AwsConfig():

    def __init__(self):
        super().__init__()
        path = os.path.join(os.path.expanduser('~'), '.aws/config')
        self.config = configparser.ConfigParser()
        self.config.read(path)

    def get_profile_names(self):
        return [section.replace('profile ', '') for section in sorted(self.config.sections())
                if 'role_arn' in self.config[section]]

    def to_console(self):
        console = Console()
        console.clear()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Profile", style="dim", width=20)
        table.add_column("Assumed Role")

        for section in sorted(self.config.sections()):
            if 'role_arn' in self.config[section]:
                table.add_row(section.replace('profile ', ''), self.config[section]["role_arn"])

        # show results
        console.print(table)


class AwsCredntials():

    def __init__(self, profile, assume_role_arn, sso_profile='azure'):
        super().__init__()
        self.aws_config_path = os.path.join(os.path.expanduser('~'), '.aws/config')
        self.boto3_session = boto3.session.Session(profile_name=sso_profile)
        self.profile = profile
        self.assume_role(assume_role_arn)

    def assume_role(self, role_arn):
        sts_client = self.boto3_session.client('sts')

        # Call the assume_role method of the STSConnection object, pass the role
        # arn to be assumed
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleCloudEngineerSession"
        )
        tmp_credentials = assumed_role_object['Credentials']
        self.aws_session_kwargs = {
            "aws_access_key_id": tmp_credentials["AccessKeyId"],
            "aws_secret_access_key": tmp_credentials["SecretAccessKey"],
            "aws_session_token": tmp_credentials["SessionToken"],
            "aws_region": 'eu-west-2',
            "aws_profile": self.profile
        }

    def create_export_command(self):

        time_stamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        with open('/tmp/aws_temp_credentials.sh', 'w') as outfile:
            outfile.write('#!/bin/bash\n')
            outfile.write('# Auto genarated aws temporary credentials\n')
            outfile.write('# run from shell source /tmp/aws_temp_credentials.sh\n')
            outfile.write(f'# genarated @ {time_stamp}\n\n')
            for aws_credential_key, aws_credential_value in self.aws_session_kwargs.items():
                command = f'export {aws_credential_key.upper()}={aws_credential_value}\n'
                outfile.write(command)
            outfile.write('\n')


@click.command()
@click.option('--profile', '-p', help='Assume the role for this Profile and Export the AWS credentials',
              prompt='Export AWS access keys',
              type=click.Choice(AwsConfig().get_profile_names(), case_sensitive=False),
              cls=QuestionaryOption)
@click.option('--sso-profile', '-s', default='azure', help='The SSO profile used to sign into AWS')
def cli(profile, sso_profile):
    """Call the aws sts service to assume the role defined in the profile
    and Export the AWS credentials environment variables

    \b
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_SESSION_TOKEN

    The profile list will be derived form .aws/config where an role_arn has been defined

    for example

    [profile squad99]
    source_profile=azure
    region=eu-west-2
    role_arn=arn:aws:iam::123456789012:role/Devloper


    run source /tmp/aws_temp_credentials.sh to export the environment variables
    """
    click.echo(f'Exporting credentials using sso profile {sso_profile} assume role defined by profile {profile}')
    aws_profile_key = f'profile {profile}'
    assumed_role_profile = AwsConfig().config[aws_profile_key]
    aws_creds = AwsCredntials(profile, assumed_role_profile['role_arn'], sso_profile)
    aws_creds.create_export_command()


if __name__ == "__main__":
    sys.exit(cli())
