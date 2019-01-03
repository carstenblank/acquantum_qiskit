from collections import OrderedDict

from providers.acquantum.acquantumerrors import AcQuantumAccountError
from providers.acquantum.credentials._env import read_credentials_from_environ
from providers.acquantum.credentials.credentials import AcQuantumCredentials


def discover_credentials():
    # type: () -> AcQuantumCredentials

    credentials = None
    readers = OrderedDict([
        ('environment variables', (read_credentials_from_environ, {}))
    ])

    for display_name, (reader_function, kwargs) in readers.items():
        try:
            credentials = reader_function(**kwargs)
            if credentials:
                break
        except AcQuantumAccountError as ex:
            print(
                'Automatic discovery of %s credentials failed: %s',
                display_name, str(ex))

    return credentials
