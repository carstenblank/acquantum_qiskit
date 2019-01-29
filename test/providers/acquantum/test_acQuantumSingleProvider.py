import os
from unittest import TestCase, mock
from unittest.mock import Mock

from acquantumconnector.credentials.credentials import AcQuantumCredentials
from providers.acquantum.acquantumsingleprovider import AcQuantumSingleProvider

backends_config = [
    {
        'backend_name': 'SIMULATE',
        'backend_version': '0.0.1',
        'n_qubits': 25,
        'basis_gates': ['XGate'],
        'gates': [
            {'name': 'u1', 'parameters': ['lambda'], 'qasm_def': 'gate u1(lambda) q { U(0,0,lambda) q; }'},
            {'name': 'u2', 'parameters': ['phi', 'lambda'],
             'qasm_def': 'gate u2(phi,lambda) q { U(pi/2,phi,lambda) q; }'},
            {'name': 'u3', 'parameters': ['theta', 'phi', 'lambda'],
             'qasm_def': 'gate u3(theta,phi,lambda) q { U(theta,phi,lambda) q; }'},
            {'name': 'cx', 'parameters': ['c', 't'], 'qasm_def': 'gate cx c,t { CX c,t; }'},
            {'name': 'id', 'parameters': ['a'], 'qasm_def': 'gate id a { U(0,0,0) a; }'},
            {'name': 'snapshot', 'parameters': ['slot'], 'qasm_def': 'gate snapshot(slot) q { TODO }'}
        ],
        'local': False,
        'simulator': True,
        'conditional': False,
        'open_pulse': False,
        'memory': False,
        'max_shots': 8192
    },
    {
        'backend_name': 'REAL',
        'backend_version': '0.0.1',
        'n_qubits': 11,
        'basis_gates': ['XGate'],
        'gates': [
            {'name': 'x',
             'parameters': [''],
             'qasm_def': ''}
        ],
        'local': False,
        'simulator': False,
        'conditional': False,
        'open_pulse': False,
        'memory': False,
        'max_shots': 20000
    }
]


class TestAcQuantumSingleProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self._cred = AcQuantumCredentials(os.environ['ACQ_USER'], os.environ['ACQ_PWD'])

    @mock.patch('providers.acquantum.acquantumsingleprovider.AcQuantumConnector.create_session')
    @mock.patch('providers.acquantum.acquantumsingleprovider.AcQuantumConnector.available_backends',
                return_value=backends_config)
    def test_init(self, available_backends, create_session):
        provider = Mock()
        AcQuantumSingleProvider(self._cred, provider)
        create_session.assert_called_once_with(self._cred)
        available_backends.assert_called_once()

    @mock.patch('providers.acquantum.acquantumsingleprovider.AcQuantumConnector.create_session')
    @mock.patch('providers.acquantum.acquantumsingleprovider.AcQuantumConnector.available_backends',
                return_value=backends_config)
    def test_backends(self, available_backends, create_session):
        provider = Mock()

        single_provider = AcQuantumSingleProvider(self._cred, provider)
        backends = list(single_provider.backends())
        self.assertEqual(len(backends), 2)
        sim, _ = backends[0]
        real, _ = backends[1]
        self.assertEqual('SIMULATE', sim)
        self.assertEqual('REAL', real)
        create_session.assert_called_once_with(self._cred)
        available_backends.assert_called_once()
