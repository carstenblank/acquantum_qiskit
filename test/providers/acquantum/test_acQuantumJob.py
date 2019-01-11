from unittest import TestCase
from unittest.mock import Mock

from providers.acquantum.acquantumerrors import AcQuantumJobError
from providers.acquantum.acquantumjob import AcQuantumJob, AcQuantumJobStatus
from providers.acquantum.models.Model import AcQuantumBackendType, AcQuantumResult, AcQuantumResultResponse


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
        self.fail()

    def test_result(self):
        self.fail()

    def test__wait_for_result(self):
        self.fail()

    def test__wait_for_job(self):
        self.fail()

    def test__check_for_submission(self):
        self.fail()

    def test_status(self):
        self.fail()

    def test__generate_job_name(self):
        self.fail()

    def test__is_job_queued(self):
        self.fail()

    def test__result_from_job_response(self):
        self.fail()
