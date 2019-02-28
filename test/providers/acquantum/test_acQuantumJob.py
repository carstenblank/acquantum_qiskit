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
from unittest import TestCase, skip
from unittest.mock import Mock

import qiskit as qiskit
from qiskit.result import Result

from acquantumconnector.model.backendtype import AcQuantumBackendType
from acquantumconnector.model.response import AcQuantumResultResponse, AcQuantumResult
from providers.acquantum.acquantumbackend import AcQuantumBackend
from providers.acquantum.acquantumerrors import AcQuantumJobError
from providers.acquantum.acquantumjob import AcQuantumJob, AcQuantumJobStatus
from providers.acquantum.acquantumprovider import AcQuantumProvider


class TestAcQuantumJob(TestCase):

    def setUp(self) -> None:
        super().setUp()

    @skip('Skip: Qobj mocking not ready')
    def test_job_id_after_submit(self):
        # Value Definition
        job_id = 1
        n_qubits = 12
        job_name = 'test'
        shots = 1000
        backend_type = AcQuantumBackendType.REAL
        # Mock Definition
        api_mock = Mock()
        api_mock.create_experiment.return_value = job_id
        api_mock.update_experiment.return_value = None
        api_mock.run_experiment.return_value = None
        qobj_mock = Mock(config=Mock(shots=shots, seeds=None), experiments=[Mock(header=Mock(qreg_sizes=[Mock()]))])
        backend_mock = Mock()
        backend_mock.configuration.return_value = Mock(n_qubits=n_qubits)
        backend_mock.backend_type.return_value = backend_type
        # Exec
        job = AcQuantumJob(backend_mock, None, api_mock, True, qobj_mock, job_name=job_name)
        job.submit()
        # Assertion
        self.assertEqual(job.job_id(), str(job_id))
        api_mock.create_experiment.assert_called_once_with(n_qubits, backend_type, job_name)
        api_mock.update_experiment.assert_called_once()
        api_mock.run_experiment.assert_called_once_with(job_id, backend_type, n_qubits, qobj_mock.config.shots,
                                                        qobj_mock.config.seeds)

    def test_job_id_failed(self):
        qobj_mock = Mock()
        job = AcQuantumJob(Mock(), None, Mock(), False, qobj_mock)
        with self.assertRaises(AcQuantumJobError):
            job.job_id()

    @skip('Skip: Qobj mocking not ready')
    def test_submit(self):
        # Value Definition
        job_id = 1
        n_qubits = 12
        job_name = 'test'
        shots = 1000
        backend_type = AcQuantumBackendType.REAL
        # Mock Definition
        api_mock = Mock()
        api_mock.create_experiment.return_value = job_id
        api_mock.update_experiment.return_value = None
        api_mock.run_experiment.return_value = None
        qobj_mock = Mock(config=Mock(shots=shots, seeds=None))
        backend_mock = Mock()
        backend_mock.configuration.return_value = Mock(n_qubits=n_qubits)
        backend_mock.backend_type.return_value = backend_type
        # Exec
        job = AcQuantumJob(backend_mock, None, api_mock, True, qobj_mock, job_name=job_name)
        job.submit()
        # Assertion
        api_mock.create_experiment.assert_called_once_with(n_qubits, backend_type, job_name)
        api_mock.update_experiment.assert_called_once_with(job_id, [])
        api_mock.run_experiment.assert_called_once_with(job_id, backend_type, n_qubits, shots, None)

    def test_cancel(self):
        api_mock = Mock()
        api_mock.get_result.return_value = AcQuantumResultResponse(
            real_result=[AcQuantumResult(result_id=12, seed=100, shots=10, start_time='2019-01-11', measure_qubits=11,
                                         finish_time=None, process="", exception=None)]
        )
        job = AcQuantumJob(None, '100', api_mock, True)
        job.cancel()
        api_mock.get_result.return_value = AcQuantumResultResponse([], [])
        self.assertEqual(AcQuantumJobStatus.CANCELLED, job.status())

    def test_status_done(self):
        api_mock = Mock()
        api_mock.get_result.return_value = AcQuantumResultResponse(
            real_result=[AcQuantumResult(result_id=12, seed=100, shots=10, start_time='2019-01-11', measure_qubits=11,
                                         finish_time='2019-01-08')])

        job = AcQuantumJob(None, '100', api_mock, True)
        status = job.status()
        self.assertEqual(status, AcQuantumJobStatus.DONE)

    def test_status_queued(self):
        api_mock = Mock()
        api_mock.get_result.return_value = AcQuantumResultResponse(
            real_result=[
                AcQuantumResult(result_id=12, seed=100, shots=10, start_time='', measure_qubits=11, process='c32c')])

        job = AcQuantumJob(None, '100', api_mock, True)
        status = job.status()
        self.assertEqual(status, AcQuantumJobStatus.QUEUED)
        self.assertEqual(job.get_queue_position(), '32')

    def test_status_error(self):
        api_mock = Mock()
        api_mock.get_result.return_value = AcQuantumResultResponse(
            real_result=[AcQuantumResult(result_id=12, seed=100, shots=10, start_time='', measure_qubits=11,
                                         finish_time='2019-01-08', exception='Error')])

        job = AcQuantumJob(None, '100', api_mock, True)
        status = job.status()
        self.assertEqual(status, AcQuantumJobStatus.ERROR)

    def test__result_from_job_response(self):
        # TODO: Implement Result
        pass

    def test_result(self):
        # TODO: Implement Result
        pass

    def test__gates_from_qobj(self):
        import qiskit.extensions.standard as standard
        from qiskit.circuit.measure import measure
        from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

        q = QuantumRegister(2, "q")
        r = QuantumRegister(1, "r")
        c = ClassicalRegister(2, "c")
        ca = ClassicalRegister(1, "c^a")
        qc = QuantumCircuit(q, c, r, ca, name="TestCircuit")
        standard.h(qc, q[0])
        standard.cx(qc, q[0], q[1])
        standard.x(qc, r)
        measure(qc, q, c)
        measure(qc, r, ca)

        provider = AcQuantumProvider()
        provider.enable_account()
        backend = provider.get_backend("SIMULATE")

        qobj = qiskit.compile(qc, backend=backend)

        gates = AcQuantumJob._gates_from_qobj(qobj)
        self.assertEqual(len(gates), 8)

    def test_submit(self):
        import qiskit.extensions.standard as standard
        from qiskit.circuit.measure import measure
        from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

        q = QuantumRegister(2, "q")
        r = QuantumRegister(1, "r")
        c = ClassicalRegister(2, "c")
        ca = ClassicalRegister(1, "c^a")
        qc = QuantumCircuit(q, r, c, ca, name="TestCircuit")
        standard.h(qc, q[0])
        standard.cx(qc, q[0], q[1])
        standard.x(qc, r)
        measure(qc, q, c)
        measure(qc, r, ca)

        provider = AcQuantumProvider()
        provider.enable_account()
        backend = provider.get_backend("SIMULATE")  # type: AcQuantumBackend

        qobj = qiskit.compile(qc, backend=backend)
        job = backend.run(qobj)  # type: AcQuantumJob
        result = job.result()  # type: Result

        self.assertIsNotNone(result)

        counts = result.get_counts()

        self.assertListEqual(list(sorted(counts.keys())), ['1 01', '1 10'])
        self.assertAlmostEqual(counts['1 01'], 512, delta=50)
        self.assertAlmostEqual(counts['1 10'], 512, delta=50)

        job._api.delete_experiment(job.job_id())

