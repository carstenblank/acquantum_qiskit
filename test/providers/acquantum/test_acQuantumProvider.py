import os
from unittest import TestCase


class TestAcQuantumProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()
        os.environ['ACQ_USER'] = 'sebboer'
        os.environ['ACQ_PWD'] = 'qnpwzHyIIFw33Nw2PBx'

    def test_load_account(self):
        pass
