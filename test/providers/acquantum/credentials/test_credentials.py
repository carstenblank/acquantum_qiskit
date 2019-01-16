import os
from unittest import TestCase

from providers.acquantum.acquantumerrors import AcQuantumAccountError
from providers.acquantum.credentials import read_credentials_from_environ, discover_credentials


class TestCredentials(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_env_reading(self):
        cred = read_credentials_from_environ()
        self.assertEqual(cred.user_name, os.environ['ACQ_USER'])
        self.assertEqual(cred.password, os.environ['ACQ_PWD'])

    def test_discover_credentials(self):
        cred = discover_credentials()
        self.assertEqual(cred.user_name, os.environ['ACQ_USER'])
        self.assertEqual(cred.password, os.environ['ACQ_PWD'])

    def test_no_credentials_discover(self):
        user = os.environ['ACQ_USER']
        pwd = os.environ['ACQ_PWD']
        del os.environ['ACQ_USER']
        del os.environ['ACQ_PWD']
        with self.assertRaises(AcQuantumAccountError):
            discover_credentials()

        os.environ['ACQ_USER'] = user
        os.environ['ACQ_PWD'] = pwd

    def test_no_credentials_from_environ(self):
        user = os.environ['ACQ_USER']
        pwd = os.environ['ACQ_PWD']
        del os.environ['ACQ_USER']
        del os.environ['ACQ_PWD']
        with self.assertRaises(AcQuantumAccountError):
            read_credentials_from_environ()

        os.environ['ACQ_USER'] = user
        os.environ['ACQ_PWD'] = pwd
