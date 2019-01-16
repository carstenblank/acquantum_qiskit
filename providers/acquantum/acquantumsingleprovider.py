from collections import OrderedDict, _OrderedDictItemsView

from jsonschema import ValidationError
from qiskit.providers import BaseProvider

from providers.acquantum.acquantumbackend import AcQuantumBackend
from providers.acquantum.acquantumconnector import AcQuantumConnector, AcQuantumCredentials
from providers.acquantum.backendconfiguration import AcQuantumBackendConfiguration


class AcQuantumSingleProvider(BaseProvider):

    def __init__(self, credentials, provider):
        # type: (AcQuantumCredentials, 'AcQuantumProvider') -> None
        super().__init__()

        self._ac_provider = provider
        self.credentials = credentials  # type: AcQuantumCredentials
        self._api = self._authenticate(self.credentials)  # type: AcQuantumConnector

        self._backends = self._discover_remote_backends()

    def backends(self, name=None, **kwargs):
        # type: (str, dict) -> _OrderedDictItemsView

        backends = self._backends.items()

        if name:
            kwargs['backend_name'] = name

        return backends

    def _discover_remote_backends(self):
        # type: () -> OrderedDict[str, AcQuantumBackend]

        ret = OrderedDict()
        configs_list = self._api.available_backends()

        for raw_config in configs_list:
            try:
                config = AcQuantumBackendConfiguration.from_dict(raw_config)
                ret[config.backend_name] = AcQuantumBackend(
                    configuration=config,
                    provider=self._ac_provider,
                    credentials=self.credentials,
                    api=self._api)
            except ValidationError as ex:
                print(
                    'Remote backend {} could not be instantiated due to an invalid config: {}'
                        .format(raw_config.get('backend_name', raw_config.get('name', 'unknown')), ex)
                )

        return ret

    @classmethod
    def _authenticate(cls, credentials):
        # type: (AcQuantumCredentials) -> AcQuantumConnector
        connector = AcQuantumConnector()
        connector.create_session(credentials)
        return connector
