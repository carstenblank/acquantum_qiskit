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
        if single_prov_mock.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   single_prov_mock._mock_name or 'mock')
            raise AssertionError(msg)
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
