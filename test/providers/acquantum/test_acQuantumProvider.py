import os
from unittest import TestCase

from providers.acquantum.acquantumprovider import AcQuantumProvider


class TestAcQuantumProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_load_account(self):
        self.provider = AcQuantumProvider()
        self.provider.load_account()
        accounts = self.provider._accounts
        self.assertTrue(os.environ['ACQ_USER'] in accounts)

    def test_get_backends(self):
        self.provider = AcQuantumProvider()
        self.provider.load_account()
        backends = self.provider.backends()
        self.assertEqual(2, len(backends))
        sim, _ = backends[0]
        real, _ = backends[1]
        self.assertEqual('SIMULATE', sim)
        self.assertEqual('REAL', real)
