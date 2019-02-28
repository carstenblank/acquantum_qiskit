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
import json
import math
import time
from enum import Enum
from typing import Any, List, Dict, Union

import qiskit
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.dagcircuit import DAGCircuit
from qiskit.providers import BaseJob, BaseBackend
from qiskit.providers.models import BackendConfiguration
from qiskit.qobj import Qobj
from qiskit.result import Result

from acquantumconnector.model.errors import AcQuantumRequestError
from acquantumconnector.model.gates import Gate
from acquantumconnector.model.response import AcQuantumResultResponse, AcQuantumResult
from acquantumconnector.connector.acquantumconnector import AcQuantumConnector
from .acquantumerrors import AcQuantumJobError
from .acquantumerrors import AcQuantumJobTimeOutError
from .models import AcQuantumExperiment


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
        # type: (AcQuantumBackend, str, AcQuantumConnector, bool, Qobj, Any, AcQuantumJobStatus, str) -> None
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

        self._api = api  # type: AcQuantumConnector
        self._backend = backend  # type: 'AcQuantumBackend'
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

        if len(self._qobj.experiments) != 1:
            raise AcQuantumJobError('The qobj must have exactly one (1) experiment.')

        if n_qubits is None:
            n_qubits = self._backend.configuration().n_qubits

        backend_type = self._backend.backend_type()

        if self._job_name is None:
            if self._qobj.experiments[0].header.name:
                self._job_name = self._qobj.experiments[0].header.name
            else:
                self._job_name = self._generate_job_name()
        job_id = None
        try:
            job_id = self._api.create_experiment(n_qubits, backend_type, self._job_name)
            self._job_id = str(job_id)

            gates = self._gates_from_qobj(self._qobj)
            self._api.update_experiment(job_id, gates, code=json.dumps(self._qobj.as_dict()))

            seed = getattr(self._qobj.config, "seed", None)
            self._api.run_experiment(job_id, experiment_type=backend_type, bit_width=n_qubits,
                                     shots=self._qobj.config.shots, seed=seed)
        except AcQuantumRequestError as e:
            if job_id is not None:
                self._api.delete_experiment(job_id)
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

    def _result_from_job_response(self, job_response):
        # type: (AcQuantumResultResponse) -> Result

        backend = self.backend()  # type: BaseBackend
        config = backend.configuration()  # type: BackendConfiguration
        experiment = self._api.get_experiment(int(self.job_id()))  # type: AcQuantumExperiment

        result_details = {}
        job_results = job_response.get_results()
        if len(job_results) == 1:
            experiment_result = job_results[0]  # type: AcQuantumResult

            counts = dict((hex(int(k, 2)), int(v * experiment_result.shots)) for k, v in experiment_result.data.items())
            self._qobj = Qobj.from_dict(json.loads(experiment.code))
            self._job_name = self._qobj.experiments[0].header.name

            success = experiment_result.exception is None

            result_details = {
                "status": self._status.name,
                "success": success,
                "name": self._job_name,
                "seed": experiment_result.seed,
                "shots": experiment_result.shots,
                "data": {
                    "counts": counts
                },
                "start_time": experiment_result.start_time,
                "finish_time": experiment_result.finish_time,
                "header": self._qobj.experiments[0].header.as_dict()
            }

        from dateutil.parser import parser
        date = parser().parse(result_details['finish_time'])

        result_dict = {
            'results': [result_details],
            'backend_name': config.backend_name,
            'backend_version': config.backend_version,
            'qobj_id': self._qobj.qobj_id,
            'job_id': str(self.job_id()),
            'success': len(job_results) == 1,
            'header': {
                "backend_name": config.backend_name
            },
            "date": date.isoformat()
        }

        result = Result.from_dict(result_dict)

        return result

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
    def _gates_from_qobj(cls, qobj):
        # type: (Qobj) -> List[Gate]
        import qiskit.extensions.standard as standard_gates
        import acquantumconnector.model.gates as ac_gates
        from qiskit.converters import qobj_to_circuits, circuit_to_dag

        qubit_labels = qobj.experiments[0].header.qubit_labels  # type: List[List[Any]]

        qc = qobj_to_circuits(qobj)  # type: QuantumCircuit
        # TODO: do all circuits.
        dag = circuit_to_dag(qc[0])  # type: DAGCircuit

        # Result
        gates = []  # type: List[Gate]

        def get_q_index(qarg):
            qubit, y = qarg
            q_index = qubit_labels.index([qubit.name, y])
            return q_index

        current_layer_x_number = 1
        layer = {}  # type: Dict[str, Union[DAGCircuit, list]]
        for layer in dag.layers():
            layer_dag = layer["graph"]  # type: DAGCircuit
            x_numbers = dict((qubit_labels.index([r.name, i]), current_layer_x_number) for r, i in layer_dag.wires
                             if isinstance(r, QuantumRegister))

            for op_node in layer_dag.get_op_nodes(data=True):
                # Given keys:
                # op_node[1]["cargs"]
                # op_node[1]["condition"]
                # op_node[1]["name"]
                # op_node[1]["qargs"]
                # op_node[1]["type"]
                # op_node[1]["op"]

                if isinstance(op_node[1]["op"], standard_gates.U1Gate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.U1Gate
                    y = get_q_index(qk_gate.qargs[0])
                    [theta] = qk_gate.param
                    gates.append(ac_gates.RzGate(x_numbers[y], y + y, theta))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.U2Gate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.U2Gate
                    y = get_q_index(qk_gate.qargs[0])
                    [phi, lam] = qk_gate.param

                    # ignore global phase alpha!
                    # alpha = lam/2 + phi/2
                    beta = phi
                    delta = lam
                    gamma = math.pi / 2
                    gates.append(ac_gates.RzGate(x_numbers[y], y + 1, delta))
                    x_numbers[y] += 1
                    gates.append(ac_gates.RyGate(x_numbers[y], y + 1, gamma))
                    x_numbers[y] += 1
                    gates.append(ac_gates.RzGate(x_numbers[y], y + 1, beta))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.U3Gate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.U3Gate
                    # I assume that all qubits have been transformed into the qubit regsiter 'q'
                    # and that the index simply tells me which wire this is.
                    [theta, phi, lam] = qk_gate.param
                    y = get_q_index(qk_gate.qargs[0])

                    # ignore global phase alpha!
                    # alpha = lam/2 + phi/2
                    beta = phi
                    delta = lam
                    gamma = theta
                    gates.append(ac_gates.RzGate(x_numbers[y], y + 1, delta))
                    x_numbers[y] += 1
                    gates.append(ac_gates.RyGate(x_numbers[y], y + 1, gamma))
                    x_numbers[y] += 1
                    gates.append(ac_gates.RzGate(x_numbers[y], y + 1, beta))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.HGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.HGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.HGate(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.RXGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.RXGate
                    y = get_q_index(qk_gate.qargs[0])
                    [theta] = qk_gate.param
                    gates.append(ac_gates.RxGate(x_numbers[y], y + 1, theta))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.RYGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.RYGate
                    y = get_q_index(qk_gate.qargs[0])
                    [theta] = qk_gate.param
                    gates.append(ac_gates.RyGate(x_numbers[y], y + 1, theta))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.RZGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.RZGate
                    y = get_q_index(qk_gate.qargs[0])
                    [theta] = qk_gate.param
                    gates.append(ac_gates.RzGate(x_numbers[y], y + 1, theta))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.XGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.XGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.XGate(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.YGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.YGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.YGate(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.ZGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.ZGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.ZGate(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.SGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.SGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.SGate(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.SdgGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.SdgGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.SDag(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.TGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.TGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.TGate(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.TdgGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.TdgGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.TDag(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.CrzGate):
                    qk_gate = op_node[1]["op"]  # type: standard_gates.CrzGate
                    y = get_q_index(qk_gate.qargs[0])
                    gates.append(ac_gates.CPhase(x_numbers[y], y + 1))
                    x_numbers[y] += 1

                elif isinstance(op_node[1]["op"], standard_gates.CnotGate):
                    cx = op_node[1]["op"]  # type: standard_gates.CnotGate
                    y1 = get_q_index(cx.qargs[0])
                    y2 = get_q_index(cx.qargs[1])
                    gates.append(ac_gates.HGate(x_numbers[y2], y2 + 1))
                    x_numbers[y1] += 1
                    x_numbers[y2] += 1
                    gates.append(ac_gates.CPhase(x_numbers[y2], [y1 + 1, y2 + 1]))
                    x_numbers[y1] += 1
                    x_numbers[y2] += 1
                    gates.append(ac_gates.HGate(x_numbers[y2], y2 + 1))
                    x_numbers[y1] += 1
                    x_numbers[y2] += 1

                elif isinstance(op_node[1]["op"], standard_gates.ToffoliGate):
                    cx = op_node[1]["op"]  # type: standard_gates.ToffoliGate
                    y1 = get_q_index(cx.qargs[0])
                    y2 = get_q_index(cx.qargs[1])
                    y3 = get_q_index(cx.qargs[2])
                    gates.append(ac_gates.HGate(x_numbers[y3], y3 + 1))
                    x_numbers[y1] += 1
                    x_numbers[y2] += 1
                    x_numbers[y3] += 1
                    gates.append(ac_gates.CCPhase(x_numbers[y3], [y1 + 1, y2 + 1, y3 + 1]))
                    x_numbers[y1] += 1
                    x_numbers[y2] += 1
                    x_numbers[y3] += 1
                    gates.append(ac_gates.HGate(x_numbers[y3], y3 + 1))
                    x_numbers[y1] += 1
                    x_numbers[y2] += 1
                    x_numbers[y3] += 1

                elif isinstance(op_node[1]["op"], qiskit.circuit.Measure):
                    measure = op_node[1]["op"]  # type: qiskit.circuit.Measure
                    y = get_q_index(measure.qargs[0])
                    gates.append(ac_gates.Measure(x_numbers[y], y + 1))
                    x_numbers[y] += 1

            current_layer_x_number = max(x_numbers.values())

        return gates
