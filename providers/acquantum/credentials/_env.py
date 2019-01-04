import os

from providers.acquantum.acquantumerrors import AcQuantumAccountError
from providers.acquantum.credentials.credentials import AcQuantumCredentials

VAR_MAP = {
    'ACQ_USER': 'user_name',
    'ACQ_PWD': 'password'
}


def read_credentials_from_environ() -> AcQuantumCredentials or None:
    if not (os.getenv('ACQ_USER') and os.getenv('ACQ_PWD')):
        raise AcQuantumAccountError('No Credentials Found in Environment')

    credentials = {}
    for envar_name, credentials_key in VAR_MAP.items():
        if os.getenv(envar_name):
            credentials[credentials_key] = os.getenv(envar_name)

    credentials = AcQuantumCredentials(**credentials)
    return credentials
