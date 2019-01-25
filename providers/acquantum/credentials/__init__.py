from acquantumconnector.credentials.credentials import AcQuantumCredentials
from providers.acquantum.acquantumerrors import AcQuantumAccountError
from providers.acquantum.credentials._env import read_credentials_from_environ


def discover_credentials() -> AcQuantumCredentials:
    credentials = None
    readers = {
        'environment variables': (read_credentials_from_environ, {}),
    }

    for display_name, (reader_function, kwargs) in readers.items():
        try:
            credentials = reader_function(**kwargs)
            if credentials:
                break
        except AcQuantumAccountError as ex:
            print('Automatic discovery of {} credentials failed: {}'.format(display_name, str(ex)))

    if credentials is None:
        raise AcQuantumAccountError('No Credentials Found')
    else:
        return credentials
