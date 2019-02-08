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

import datetime
import time
from enum import Enum
from typing import Any, List

import qiskit
from acquantumconnector.model.errors import AcQuantumRequestError
from acquantumconnector.model.gates import Gate, CPhase, HGate
from acquantumconnector.model.response import AcQuantumResultResponse, AcQuantumResult
from qiskit import QuantumCircuit
from qiskit.dagcircuit import DAGCircuit
from qiskit.extensions.standard import U2Gate, U3Gate, U1Gate, CnotGate
from qiskit.providers import BaseJob
from qiskit.qobj import Qobj, QobjConfig, QobjHeader
from qiskit.result import Result

from providers.acquantum.acquantumerrors import AcQuantumJobError
from providers.acquantum.acquantumerrors import AcQuantumJobTimeOutError


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

    def __init__(self, backend, job_id, api, is_device, qobj=None, creation_date=None, api_status=None, job_name=None):
        # type: ('AcQuantumBackend', str, 'AcQuantumConnector', bool, Qobj, Any, AcQuantumJobStatus, str) -> None
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
            # validate_qobj_against_schema(qobj)
            self._qobj = qobj

        self._api = api
        self._backend = backend
        self._cancelled = False
        self._status = AcQuantumJobStatus.INITIALIZING
        self._job_name = job_name
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

    def submit(self, n_qubits=None):
        # type: (int) -> None

        if self._qobj is None:
            raise AcQuantumJobError('Can not find qobj')

        if n_qubits is None:
            n_qubits = self._backend.configuration().n_qubits

        backend_type = self._backend.backend_type()

        if self._job_name is None:
            self._job_name = self._generate_job_name()
        try:
            job_id = self._api.create_experiment(n_qubits, backend_type, self._job_name)
            self._job_id = str(job_id)

            gates = self._gates_from_qobj(self._qobj)

            self._api.update_experiment(job_id, gates)
            self._api.run_experiment(job_id, backend_type, n_qubits, self._qobj.config.shots,
                                     self._qobj.config.seeds)  # TODO HANDLE INPUT
        except AcQuantumRequestError as e:
            raise AcQuantumJobError(e.message)

    def cancel(self):
        # type: () -> bool
        """
        :return: bool: True if job can be cancelled else False.
        :raises: AcQuantumJobError: if there was some unexpected failure in the server
        """
        try:
            # self._api.del(experiment_id=int(self._job_id))
            status = self.status()
            if status is AcQuantumJobStatus.QUEUED:
                result = self._api.get_result(int(self.job_id())).get_results()
                if result:
                    self._api.delete_result(result[-1].result_id)
                    self._status = AcQuantumJobStatus.CANCELLED
                    return True
            else:
                return False
        except AcQuantumRequestError as ex:
            self._status = AcQuantumJobStatus.ERROR
            raise AcQuantumJobError('Error canceling job: {}'.format(ex.message))

    def result(self, timeout=None, wait=5):
        # type: (int, int) -> Result
        """
        Return the result from the job.
        :param timeout: number of seconds to wait for job
        :param wait: time between queries to Alibaba Computing Quantum
        :return: qiskit.Result
        """
        job_response = self._wait_for_result(timeout=timeout, wait=5)
        return self._result_from_job_response(job_response)

    def _wait_for_result(self, timeout=None, wait=5):
        # type: (int, int) -> AcQuantumResultResponse
        self._check_for_submission()
        try:
            job_response = self._wait_for_job(timeout=timeout, wait=wait)
        except AcQuantumRequestError:
            raise AcQuantumJobError('Result query failed')
        status = self.status()
        if status is not AcQuantumJobStatus.DONE:
            raise AcQuantumJobError('Invalid job state. The job should be DONE but it is {}'.format(str(status)))
        return job_response

    def _wait_for_job(self, timeout, wait):
        # type: (int, int) -> AcQuantumResultResponse
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

    def status(self):
        # type: () -> AcQuantumJobStatus
        """
        Query the Api to update the status of the job
        :return: The status of the job, once updated
        :raises: AcQuantumJobError: if there was an unknown answer from the server
        """
        if self._status is AcQuantumJobStatus.CANCELLED:
            return self._status

        try:
            result = self._api.get_result(experiment_id=int(self._job_id)).get_results()
            if not result:
                self._status = AcQuantumJobStatus.QUEUED
            else:
                result = result[-1]
        except AcQuantumRequestError as e:
            print(e)
            self._status = AcQuantumJobStatus.ERROR
            return self._status

        if not result.finish_time:
            self._status = AcQuantumJobStatus.RUNNING
            queued, self._queue_position = self._is_job_queued(result)
            if queued:
                self._status = AcQuantumJobStatus.QUEUED
        elif result.exception:
            self._status = AcQuantumJobStatus.ERROR
        elif result.finish_time:
            self._status = AcQuantumJobStatus.DONE
        else:
            raise AcQuantumJobError('Unrecognized answer from server: \n{}'.format(result))
        return self._status

    def _generate_job_name(self):
        # type: () -> str
        return 'Qiskit_generated_{}'.format(self._creation_date)

    @classmethod
    def _is_job_queued(cls, result):
        # type: (AcQuantumResult) -> (bool, int)
        """Checks whether a job has been queued or not."""
        is_queued, position = False, 0
        if not result.finish_time:
            is_queued = True
            position = result.process[1:-1]  # TODO CHECK ATTRIBUTE
        return is_queued, position

    def get_queue_position(self):
        return self._queue_position

    @classmethod
    def _result_from_job_response(cls, job_response):
        # type: (AcQuantumResultResponse) -> Result
        # TODO: Implement qiskit.Result
        return None

    @classmethod
    def _gates_from_qobj(cls, qobj):
        # type: (Qobj) -> List[Gate]

        id = qobj.qobj_id  # type: str
        config = qobj.config  # type: QobjConfig
        header = qobj.header  # type: QobjHeader
        # I will most likely not use the following fields...
        # TODO: remove when done
        # experiments = qobj.experiments  # type: List[QobjExperiment]
        # for experiment in experiments:
        #     exp_header = experiment.header  # type: QobjItem
        #     exp_header.clbit_labels  # type: List[Tuple[str, int]]
        #     exp_header.qubit_labels  # type: List[Tuple[str, int]]
        #     exp_header.creg_sizes  # type: List[Tuple[str, int]]
        #     exp_header.qreg_sizes  # type: List[Tuple[str, int]]
        #     exp_header.memory_slots  # type: int
        #     exp_header.n_qubits  # type: int
        #     exp_header.name  # type: str
        #     exp_header.compiled_circuit_qasm  # type: str
        #
        #     # every element has fields: memory: List[int], name: str, params: List[float], qubits: List[int], texparams: List[str]
        #     exp_instr = experiment.instructions  # type: List[QobjItem]

        from qiskit.converters import qobj_to_circuits, circuit_to_dag

        qc = qobj_to_circuits(qobj)  # type: QuantumCircuit
        dag = circuit_to_dag(qc)  # type: DAGCircuit

        layer = {}  # type: dict
        for layer in dag.layers():
            layer_dag = layer["graph"]  # type: DAGCircuit

            gates = []  # type: List[Gate]
            x = 0
            for op_node in layer_dag.get_op_nodes():
                # Given keys:
                # op_node[1]["cargs"]
                # op_node[1]["condition"]
                # op_node[1]["name"]
                # op_node[1]["qargs"]
                # op_node[1]["type"]
                # op_node[1]["op"]

                if isinstance(op_node[1]["op"], U2Gate):
                    u2 = op_node[1]["op"]  # type: U2Gate
                    # I assume that all qubits have been transformed into the qubit regsiter 'q'
                    # and that the index simply tells me which wire this is.
                    qubit, y = u2.qargs[0]  # Tuple[QuantumRegister, int]
                    # TODO
                elif isinstance(op_node[1]["op"], U1Gate):
                    u1 = op_node[1]["op"]  # type: U1Gate
                    # I assume that all qubits have been transformed into the qubit regsiter 'q'
                    # and that the index simply tells me which wire this is.
                    qubit, y = u1.qargs[0]
                    # TODO
                elif isinstance(op_node[1]["op"], U3Gate):
                    u3 = op_node[1]["op"]  # type: U3Gate
                    # I assume that all qubits have been transformed into the qubit regsiter 'q'
                    # and that the index simply tells me which wire this is.
                    qubit, y = u3.qargs[0]
                    # TODO
                elif isinstance(op_node[1]["op"], CnotGate):
                    cx = op_node[1]["op"]  # type: CnotGate
                    # I assume that all qubits have been transformed into the qubit regsiter 'q'
                    # and that the index simply tells me which wire this is.
                    ctr, y1 = cx.qargs[0]
                    tgt, y2 = cx.qargs[1]
                    gates.append(HGate(x, y2))
                    gates.append(CPhase(x, [y1, y2]))
                    gates.append(HGate(x, y2))
                elif isinstance(op_node[1]["op"], qiskit.circuit.Measure):
                    measure = op_node[1]["op"]  # type: qiskit.circuit.Measure
                    qubit, y = measure.qargs[0]
                    # TODO

                x += 1

        # TODO: Implement Qobj to Gates
        return []
