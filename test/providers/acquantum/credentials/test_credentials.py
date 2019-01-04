import os
from unittest import TestCase

from providers.acquantum.acquantumerrors import AcQuantumAccountError
from providers.acquantum.credentials import read_credentials_from_environ, discover_credentials


class TestCredentials(TestCase):

    def setUp(self) -> None:
        super().setUp()
        os.environ['ACQ_USER'] = 'test'
        os.environ['ACQ_PWD'] = 'secure'

    def test_env_reading(self):
        cred = read_credentials_from_environ()
        self.assertEqual(cred.user_name, 'test')
        self.assertEqual(cred.password, 'secure')

    def test_discover_credentials(self):
        cred = discover_credentials()
        self.assertEqual(cred.password, 'secure')
        self.assertEqual(cred.user_name, 'test')

    def test_no_credentials_discover(self):
        del os.environ['ACQ_USER']
        del os.environ['ACQ_PWD']
        with self.assertRaises(AcQuantumAccountError):
            discover_credentials()

    def test_no_credentials_from_environ(self):
        del os.environ['ACQ_USER']
        del os.environ['ACQ_PWD']
        with self.assertRaises(AcQuantumAccountError):
            read_credentials_from_environ()
