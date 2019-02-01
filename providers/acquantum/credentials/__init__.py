#  Copyright (c) 2019.  Carsten Blank
# 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
