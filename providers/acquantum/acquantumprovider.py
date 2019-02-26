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

import warnings
from collections import OrderedDict

from qiskit.providers import BaseProvider

from acquantumconnector.credentials.credentials import AcQuantumCredentials
from .acquantumbackend import AcQuantumBackend
from .acquantumerrors import AcQuantumAccountError, AcQuantumBackendError
from .acquantumsingleprovider import AcQuantumSingleProvider
from .credentials import discover_credentials


class AcQuantumProvider(BaseProvider):

    def __init__(self):
        super().__init__()

        self._accounts = OrderedDict()

    def backends(self, name=None, **kwargs):
        # type: (str, dict) -> [AcQuantumBackend]
        """
        :param name: name of the backend
        :param kwargs: kwargs for filtering not yet implemented
        :return:
        """

        providers = [provider for provider in self._accounts.values()]

        # Aggregate the list of filtered backends.
        backends = []
        for provider in providers:
            backends = backends + list(provider.backends(
                name=name, **kwargs))

        if not backends:
            raise AcQuantumBackendError('zero backends found')
        return backends

    def load_account(self, credentials=None):
        if credentials is None:
            self._append_account(discover_credentials())
        else:
            self._append_account(credentials)

        if not self._accounts:
            raise AcQuantumAccountError('No AcQuantum credentials found.')

    def _append_account(self, credentials: AcQuantumCredentials):
        if credentials.user_name in self._accounts.keys():
            warnings.warn('Credentials are already in use.')

        single_provider = AcQuantumSingleProvider(credentials, self)
        self._accounts[credentials.user_name] = single_provider

    @staticmethod
    def _aliased_backend_names(self):
        pass

    @staticmethod
    def _deprecated_backend_names(self):
        pass
