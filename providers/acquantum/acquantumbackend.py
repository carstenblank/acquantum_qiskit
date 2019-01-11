from qiskit.providers import BaseBackend

from providers.acquantum.acquantumconnector import AcQuantumConnector
from providers.acquantum.acquantumerrors import AcQuantumError, AcQuantumBackendError
from providers.acquantum.acquantumjob import AcQuantumJob
from providers.acquantum.backendconfiguration import AcQuantumBackendConfiguration
from providers.acquantum.credentials import AcQuantumCredentials
from providers.acquantum.models.Model import AcQuantumBackendType, AcQuantumRequestError


class AcQuantumBackend(BaseBackend):

    def __init__(self, configuration, provider, credentials, api):
        # type: (AcQuantumBackendConfiguration, AcQuantumProvider, AcQuantumCredentials, AcQuantumConnector) -> None
        """
        :param configuration: configuration of backend
        :param provider:
        :param credentials:
        :param api: api for communicating with Alibaba Computing Quantum
        """
        super().__init__(provider=provider, configuration=configuration)

        self._api = api
        self._credentials = credentials
        try:
            self._backend_type = AcQuantumBackendType[configuration.backend_name]
        except KeyError:
            raise AcQuantumError('Unknown Backend Name')

    def run(self, qobj, job_name=None):
        # type: (qiskit.Qobj, str) -> AcQuantumJob
        """Run qobj

        Args:
            qobj (Qobj): description of job
            job_name (str): job name

        Returns:
            AcQuantumJob: an instance derived from BaseJob
        """
        job = AcQuantumJob(self, None, self._api, not self.configuration().simulator, qobj=qobj, job_name=job_name)
        job.submit()
        return job

    def properties(self):
        # TODO: Implement backend properties
        pass

    def status(self):
        # TODO: Implement backend status
        if self._is_device():
            res = self._api.get_backend_config()

    def jobs(self, limit=50, skip=0):
        # type: (int, int) -> [AcQuantumJob]
        """

        :param limit: number of jobs to retrieve
        :param skip: starting index of retrieval
        :return: list of AcQuantumJob instances
        :raises: AcQuantumRequestError
        """

        job_info_list = self._api.get_experiments()

        jobs = []

        for job in job_info_list:
            if job.experiment_type is self._backend_type:
                jobs.append(AcQuantumJob(self, job.experiment_id, self._api, self._is_device(), job_name=job.name))

        if skip:
            jobs = jobs[skip:]

        return jobs[:limit]

    def retrieve_job(self, job_id):
        # type: (str) -> AcQuantumJob
        """
        :param job_id: job id of the job to retrieve
        :return: job: AcQuantum Job
        :raises: AcQuantumBackendError: if retrieval fails
        """
        try:
            response = self._api.get_experiment(int(job_id))
        except AcQuantumRequestError as ex:
            raise AcQuantumBackendError('Failed to get job "{}" {}'.format(job_id, str(ex)))

        return AcQuantumJob(self, response.detail.experiment_id, self._api, self._is_device(),
                            job_name=response.detail.name)

    def _is_device(self):
        # type: () -> bool
        return not bool(self.configuration().simulator)

    def backend_type(self):
        return self._backend_type
