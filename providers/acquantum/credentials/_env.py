import os
from collections import OrderedDict

from providers.acquantum.credentials.credentials import AcCredentials

VAR_MAP = {
    'ACQ_USER': 'user_name',
    'ACQ_PWD': 'password'
}


def read_credentials_from_environ():
    if not (os.getenv('ACQ_USER') and os.getenv('ACQ_PWD')):
        return OrderedDict()

    credentials = {}
    for envar_name, credentials_key in VAR_MAP.items():
        if os.getenv(envar_name):
            credentials[credentials_key] = os.getenv(envar_name)

    credentials = AcCredentials(**credentials)
    return credentials
