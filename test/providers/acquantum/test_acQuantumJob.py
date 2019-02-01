from unittest import TestCase
from unittest.mock import Mock

from acquantumconnector.model.backendtype import AcQuantumBackendType
from acquantumconnector.model.response import AcQuantumResultResponse, AcQuantumResult
from providers.acquantum.acquantumerrors import AcQuantumJobError
from providers.acquantum.acquantumjob import AcQuantumJob, AcQuantumJobStatus


class TestAcQuantumJob(TestCase):

    def setUp(self) -> None:
        super().setUp()

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
        qobj_mock = Mock(config=Mock(shots=shots, seeds=None))
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
                                         finish_time=None, process="")]
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
