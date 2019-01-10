import os
from unittest import TestCase

from providers.acquantum.acquantumprovider import AcQuantumProvider


class TestAcQuantumProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()
        os.environ['ACQ_USER'] = 'sebboer'
        os.environ['ACQ_PWD'] = 'qnpwzHyIIFw33Nw2PBx'

    def test_load_account(self):
        self.provider = AcQuantumProvider()
        self.provider.load_account()

    def test_get_backends(self):
        self.provider = AcQuantumProvider()
        self.provider.load_account()
        self.assertEqual(2, len(self.provider.backends()))
