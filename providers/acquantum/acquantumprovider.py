import warnings
from collections import OrderedDict

from qiskit.providers import BaseProvider

from providers.acquantum.acquantumerrors import AcQuantumAccountError
from providers.acquantum.acquantumsingleprovider import AcQuantumSingleProvider
from providers.acquantum.credentials import discover_credentials, AcQuantumCredentials


class AcQuantumProvider(BaseProvider):

    def __init__(self):
        super().__init__()

        self._accounts = OrderedDict()

    def backends(self, name=None, filters=None, **kwargs):
        # TODO: add typings
        # credentials_filter = {}
        # for key in ['token', 'url', 'hub', 'group', 'project', 'proxies', 'verify']:
        #     if key in kwargs:
        #         credentials_filter[key] = kwargs.pop(key)
        # TODO FILTER BACKENDS

        providers = [provider for provider in self._accounts.values()]

        # Aggregate the list of filtered backends.
        backends = []
        for provider in providers:
            backends = backends + provider.backends(
                name=name, filters=filters, **kwargs)

        return backends

    def load_account(self):
        self._append_account(discover_credentials())

        if not self._accounts:
            raise AcQuantumAccountError('No AcQuantum credentials found.')

    def _append_account(self, credentials):
        # type: (AcQuantumCredentials) -> None

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
