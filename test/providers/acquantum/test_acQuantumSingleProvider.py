import os
from unittest import TestCase
from unittest.mock import Mock

from providers.acquantum.acquantumsingleprovider import AcQuantumSingleProvider
from providers.acquantum.credentials import AcQuantumCredentials


class TestAcQuantumSingleProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self._cred = AcQuantumCredentials(os.environ['ACQ_USER'], os.environ['ACQ_PWD'])

    def test_init(self):
        pass

    def test_backends(self):
        provider = Mock()

        single_provider = AcQuantumSingleProvider(self._cred, provider)
        backends = list(single_provider.backends())
        self.assertEqual(len(backends), 2)
        sim, _ = backends[0]
        real, _ = backends[1]
        self.assertEqual('SIMULATE', sim)
        self.assertEqual('REAL', real)
