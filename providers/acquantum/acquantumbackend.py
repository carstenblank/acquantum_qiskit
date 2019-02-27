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

from qiskit.providers import BaseBackend
from qiskit.qobj import Qobj

from acquantumconnector.connector.acquantumconnector import AcQuantumConnector
from acquantumconnector.credentials.credentials import AcQuantumCredentials
from acquantumconnector.model.backendtype import AcQuantumBackendType
from acquantumconnector.model.errors import AcQuantumRequestError
from .acquantumerrors import AcQuantumError, AcQuantumBackendError
from .acquantumjob import AcQuantumJob
from .backendconfiguration import AcQuantumBackendConfiguration


class AcQuantumBackend(BaseBackend):

    def __init__(self, configuration, provider, credentials, api):
        # type: (AcQuantumBackendConfiguration, 'AcQuantumProvider', AcQuantumCredentials, AcQuantumConnector) -> None
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
        # type: (Qobj, str) -> AcQuantumJob
        job = AcQuantumJob(self, None, self._api, not self.configuration().simulator, qobj=qobj, job_name=job_name)
        job.submit()
        return job

    def properties(self):
        # TODO: Implement backend properties
        pass

    def status(self):
        if self._is_device():
            return self._api.get_backend_config().system_status

        raise AcQuantumBackendError('Could not find status for Simulator')

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
