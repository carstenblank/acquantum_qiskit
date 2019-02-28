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

from unittest import TestCase
from unittest.mock import Mock

from acquantumconnector.credentials.credentials import AcQuantumCredentials
from acquantumconnector.model.backendtype import AcQuantumBackendType
from acquantumconnector.model.response import AcQuantumResult, AcQuantumResultResponse

from acquantum_qiskit.acquantumbackend import AcQuantumBackend
from acquantum_qiskit.backendconfiguration import AcQuantumBackendConfiguration
from acquantum_qiskit.models import AcQuantumExperimentDetail


class TestAcQuantumBackend(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_run(self):
        pass

    def test_properties(self):
        pass

    def test_jobs(self):
        api_mock = Mock()
        jobs = [AcQuantumExperimentDetail('test', 1, 123, AcQuantumBackendType.SIMULATE, 0, 11)]
        backend_config = {
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
        }
        config = AcQuantumBackendConfiguration.from_dict(backend_config)
        api_mock.get_experiments.return_value = jobs
        api_mock.get_result.return_value = AcQuantumResultResponse(
            simulated_result=[
                AcQuantumResult(result_id=12, seed=100, shots=10, start_time='2019-01-11', measure_qubits=11,
                                finish_time=None, process="", exception=None)]
        )
        cred = AcQuantumCredentials('', '')
        backend = AcQuantumBackend(config, None, cred, api_mock)
        jobs = backend.jobs()
        self.assertEqual(jobs[0].job_id(), 123)
