import datetime
import time
from enum import Enum
from typing import Any

from qiskit.providers import BaseJob
from qiskit.qobj import qobj_to_dict, Qobj
from qiskit.qobj import validate_qobj_against_schema
from qiskit.result import Result

from providers.acquantum.acquantumbackend import AcQuantumBackend
from providers.acquantum.acquantumconnector import AcQuantumConnector
from providers.acquantum.acquantumerrors import AcQuantumJobError
from providers.acquantum.acquantumerrors import AcQuantumJobTimeOutError
from providers.acquantum.models import AcQuantumResult, AcQuantumRequestError, AcQuantumResultResponse


class AcQuantumJobStatus(Enum):
    """Class for job status enumerated type."""
    INITIALIZING = 'job is being initialized'
    QUEUED = 'job is queued'
    VALIDATING = 'job is being validated'
    RUNNING = 'job is actively running'
    CANCELLED = 'job has been cancelled'
    DONE = 'job has successfully run'
    ERROR = 'job incurred error'


JOB_FINAL_STATES = (
    AcQuantumJobStatus.DONE,
    AcQuantumJobStatus.CANCELLED,
    AcQuantumJobStatus.ERROR
)


class AcQuantumJob(BaseJob):
    """
        Represent the jobs that will be executed on Alibaba Computing Quantum simulators and real
        devices. Jobs are intended to be created calling ``run()`` on a particular
        backend.

        Creating a ``AcQuantumJob`` instance does not imply running it. You need to do it in separate steps::

            job = AcQuantumJob(..)
            job.submit() # will block!
    """

    def __init__(self, backend: AcQuantumBackend, job_id: str, api: AcQuantumConnector, is_device: bool,
                 qobj: Qobj = None,
                 creation_date: Any = None, api_status: AcQuantumJobStatus = None):
        """
        :param backend: The backend instance used to run this job
        :param job_id: The job ID of an already submitted job
        :param api: api for communicating with Alibaba Computing Quantum
        :param is_device: whether backend is a real device
        :param qobj: Quantum Object
        :param creation_date:
        :param api_status:


        """

        super().__init__(backend, job_id)

        if qobj is not None:
            validate_qobj_against_schema(qobj)

            self._qobj_payload = qobj_to_dict(qobj, version='1.0.0')
            # TODO: No need for this conversion, just use the new equivalent members above
            old_qobj = qobj_to_dict(qobj, version='0.0.1')
            self._job_data = {
                'circuits': old_qobj['circuits'],
                'hpc': old_qobj['config'].get('hpc'),
                'seed': old_qobj['circuits'][0]['config']['seed'],
                'shots': old_qobj['config']['shots'],
                'max_credits': old_qobj['config']['max_credits']
            }
        else:
            self._qobj_payload = {}

        self._api = api
        self._backend = backend
        self._cancelled = False
        self._status = AcQuantumJobStatus.INIT
        # In case of not providing a `qobj`, it is assumed the job already
        # exists in the API (with `job_id`).

        if qobj is None:
            # Some API calls (`get_status_jobs`, `get_status_job`) provide
            # enough information to recreate the `Job`. If that is the case, try
            # to make use of that information during instantiation, as
            # `self.status()` involves an extra call to the API.
            if api_status == 'VALIDATING':
                self._status = AcQuantumJobStatus.VALIDATING
            elif api_status == 'COMPLETED':
                self._status = AcQuantumJobStatus.DONE
            elif api_status == 'CANCELLED':
                self._status = AcQuantumJobStatus.CANCELLED
                self._cancelled = True
            else:
                self.status()
        self._queue_position = None
        self._is_device = is_device

        def current_utc_time():
            """Gets the current time in UTC format"""
            datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

        self._creation_date = creation_date or current_utc_time()
        self._api_error_msg = None

    def job_id(self):
        self._check_for_submission()
        return self._job_id

    def submit(self) -> None:
        try:
            job_id = self._api.create_experiment(None, None, self._generate_job_name())  # TODO CREATE EXPERIMENT
            self._job_id = str(job_id)
            self._api.update_experiment(int(self._job_id), None)  # TODO HANDLE INPUT
            self._api.run_experiment(self._job_id, None, )  # TODO HANDLE INPUT
        except AcQuantumRequestError as e:
            # TODO: handle error
            pass

    def cancel(self) -> bool:
        """
        THIS METHOD DELETES THE JOB
        JOB CANCELING IS NOT IMPLEMENTED YET

        :return: bool: True if job can be cancelled else False. Currently this is
        :raises: AcQuantumJobError: if there was some unexpected failure in the server
        """
        try:
            self._api.delete_experiment(experiment_id=int(self._job_id))
            return True
        except AcQuantumRequestError as ex:
            raise AcQuantumJobError('Error canceling job: {}'.format(ex.message))

    def result(self, timeout=None, wait=5):
        """
        Return the result from the job.
        :param timeout: number of seconds to wait for job
        :param wait: time between queries to Alibaba Computing Quantum
        :return: qiskit.Result
        """
        job_response: AcQuantumResultResponse = self._wait_for_result(timeout=timeout, wait=5)
        return self._result_from_job_response(job_response)

    def _wait_for_result(self, timeout=None, wait=5) -> AcQuantumResultResponse:
        self._check_for_submission()
        try:
            job_response: AcQuantumResultResponse = self._wait_for_job(timeout=timeout, wait=wait)
            if not self._qobj_payload:
                self._qobj_payload = job_response.get('qObject', {})  # TODO: Convert AcQuantumResultResponse to Qobj
        except AcQuantumRequestError:
            raise AcQuantumJobError('Result query failed')
        status = self.status()
        if status is not AcQuantumJobStatus.DONE:
            raise AcQuantumJobError('Invalid job state. The job should be DONE but it is {}'.format(str(status)))
        return job_response

    def _wait_for_job(self, timeout: int, wait: int) -> AcQuantumResultResponse:
        start_time = time.time()
        while self.status() not in JOB_FINAL_STATES:
            elapsed_time = time.time() - start_time
            if timeout is not None and elapsed_time >= timeout:
                raise AcQuantumJobTimeOutError('Timeout while waiting for the job: {}'.format(self._job_id))

            time.sleep(wait)
        if self._cancelled:
            raise AcQuantumJobError('Job result impossible to retrieve. The job was cancelled')

        return self._api.get_result(int(self._job_id))

    def _check_for_submission(self):
        """
        Check if Job was already submitted
        """
        if self._job_id is None:
            raise AcQuantumJobError('You have to submit before asking status or results')

    def status(self) -> AcQuantumJobStatus:
        """
        Query the Api to update the status of the job
        :return: The status of the job, once updated
        :raises: AcQuantumJobError: if there was an unknown answer from the server
        """
        try:
            result: AcQuantumResult = self._api.get_result(experiment_id=int(self._job_id)).get_result()
        except AcQuantumRequestError as e:
            self._status = AcQuantumJobStatus.ERROR
            return self._status

        # TODO: Add Validating Status
        # TODO: Add Cancelled Status
        # TODO: Add Error Status

        if not result.finish_time:
            self._status = AcQuantumJobStatus.RUNNING
            queued, self._queue_position = self._is_job_queued(result)
            if queued:
                self._status = AcQuantumJobStatus.QUEUED
        elif result.finish_time:
            self._status = AcQuantumJobStatus.DONE
        elif result.exception:
            self._status = AcQuantumJobStatus.ERROR
        else:
            raise AcQuantumJobError('Unrecognized answer from server: \n{}'.format(result))
        return self._status

    def _generate_job_name(self) -> str:
        return 'Qiskit_generated_{}'.format(self._creation_date)

    @classmethod
    def _is_job_queued(cls, result: AcQuantumResult) -> (bool, int):
        """Checks whether a job has been queued or not."""
        is_queued, position = False, 0
        if not result.finish_time:
            is_queued = True
            position = result[1:-1]
        return is_queued, position

    @classmethod
    def _result_from_job_response(cls, job_response: AcQuantumResultResponse) -> Result:
        # TODO: Implement qiskit.Result
        return None