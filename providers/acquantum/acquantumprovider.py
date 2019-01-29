import warnings
from collections import OrderedDict

from qiskit.providers import BaseProvider

from acquantumconnector.credentials.credentials import AcQuantumCredentials
from providers.acquantum.acquantumbackend import AcQuantumBackend
from providers.acquantum.acquantumerrors import AcQuantumAccountError, AcQuantumBackendError
from providers.acquantum.acquantumsingleprovider import AcQuantumSingleProvider
from providers.acquantum.credentials import discover_credentials


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

    def load_account(self):
        self._append_account(discover_credentials())

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
