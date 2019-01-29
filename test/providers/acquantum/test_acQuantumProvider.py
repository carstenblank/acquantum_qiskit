import os
from unittest import TestCase, mock

from providers.acquantum.acquantumerrors import AcQuantumBackendError
from providers.acquantum.acquantumprovider import AcQuantumProvider


class SingleMock:

    def __init__(self, credentials, provider):
        self.provider = provider
        self.credentials = credentials

    def authenticate(self):
        print(self.credentials)
        print('auth called')

    def backends(self, name=None, **kwargs):
        print('backends called')
        if self.credentials:
            return [mock.Mock(), mock.Mock()]
        else:
            return []


class TestAcQuantumProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()

    @mock.patch('providers.acquantum.acquantumprovider.AcQuantumSingleProvider', side_effect=SingleMock)
    def test_load_account(self, single_prov_mock):
        self.provider = AcQuantumProvider()
        self.provider.load_account()
        accounts = self.provider._accounts
        self.assertTrue(os.environ['ACQ_USER'] in accounts)
        single_prov_mock.assert_called()
        single_prov_mock.backends.assert_not_called()

    @mock.patch('providers.acquantum.acquantumprovider.AcQuantumSingleProvider', side_effect=SingleMock)
    def test_get_backends(self, single_prov_mock):
        self.provider = AcQuantumProvider()
        self.provider.load_account()
        backends = self.provider.backends()
        self.assertEqual(2, len(backends))

    @mock.patch('providers.acquantum.acquantumprovider.AcQuantumSingleProvider', side_effect=SingleMock)
    def test_get_backends_without_loading_accounts(self, single_prov_mock):
        provider = AcQuantumProvider()
        with self.assertRaises(AcQuantumBackendError):
            provider.backends()
            single_prov_mock.backends.assert_called_once()
