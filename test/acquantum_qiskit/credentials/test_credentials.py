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
from unittest import TestCase

from acquantum_qiskit.acquantumerrors import AcQuantumAccountError
from acquantum_qiskit.credentials import read_credentials_from_environ, discover_credentials


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
