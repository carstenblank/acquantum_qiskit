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

import os

from acquantumconnector.credentials.credentials import AcQuantumCredentials
from providers.acquantum.acquantumerrors import AcQuantumAccountError

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
