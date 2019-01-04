from unittest import TestCase

from providers.acquantum.credentials import AcQuantumCredentials


class TestAcQuantumSingleProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self._cred = AcQuantumCredentials('sebboer', 'qnpwzHyIIFw33Nw2PBx')

    def test_init(self):
        pass
