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

import json
from enum import Enum
from typing import Any


class AcQuantumBackendType(Enum):
    REAL = 'REAL',
    SIMULATE = 'SIMULATE'


class AcQuantumRequestError(Exception):
    def __init__(self, message, status_code=None):
        # type: (str, int) -> None
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return 'AcRequestError: \'{}\''.format(self.message)

    def __repr__(self):
        return 'AcRequestError: \'{}\''.format(self.message)


class AcQuantumRequestForbiddenError(AcQuantumRequestError):
    def __init__(self, message='403 Forbidden'):
        # type: (str) -> None
        self.message = message

    def __str__(self):
        return '403 - AcRequestForbiddenError: \'{}\''.format(self.message)

    def __repr__(self):
        return '403 - AcRequestForbiddenError: \'{}\''.format(self.message)


class AcQuantumResponse:
    def __init__(self, success=True, data=None, exception=None):
        # type: (bool,Any, Any) -> None
        self.success = success
        self.data = data
        self.exception = exception

    def __str__(self):
        return 'AcResponse: {{ success: {}, exception: {} }}'.format(self.success, self.exception)

    def __repr__(self):
        return 'AcResponse: {{ success: {}, exception: {} }}'.format(self.success, self.exception)


class AcQuantumErrorResponse(AcQuantumResponse):

    def __init__(self, success=False, exception=None, status_code=None):
        # type: (bool, Any, int) -> None
        super(AcQuantumErrorResponse, self).__init__()
        self.status_code = status_code
        self.success = success
        self.exception = exception

    def __str__(self):
        return 'AcErrorResponse: {{ success: {}, exception: {}, status_code: {} }}'.format(self.success, self.exception,
                                                                                           self.status_code)

    def __repr__(self):
        return 'AcErrorResponse: {{ success: {}, exception: {}, status_code: {} }}'.format(self.success, self.exception,
                                                                                           self.status_code)


class AcQuantumExperimentDetail:

    def __init__(self, name, version, experiment_id, experiment_type, execution, bit_width=None):
        # type: (str, int, int, AcQuantumBackendType, int, int) -> None
        self.name = name
        self.version = version
        self.experiment_id = experiment_id
        self.experiment_type = experiment_type
        self.execution = execution
        self.bit_width = bit_width

    def __str__(self):
        return 'AcExperimentDetail: {{ name: {}, version: {}, experiment_id: {}, experiment_type: {}, execution: {}, ' \
               'bit_width {} }}' \
            .format(self.name, self.version, self.experiment_id, self.experiment_type, self.execution, self.bit_width)

    def __repr__(self):
        return 'AcExperimentDetail: {{ name: {}, version: {}, experiment_id: {}, experiment_type: {}, execution: {}, ' \
               'bit_width {} }}' \
            .format(self.name, self.version, self.experiment_id, self.experiment_type, self.execution, self.bit_width)


class AcQuantumExperiment:

    def __init__(self, detail, data, code=''):
        # type: (AcQuantumExperimentDetail, Any, str) -> None
        self.detail = detail
        self.data = data
        self.code = code

    def __str__(self):
        return 'AcExperiment: {{ data: {}, code: {}, detail: {} }}'.format(self.data, self.code, self.detail)

    def __repr__(self):
        return 'AcExperiment: {{ data: {}, code: {}, detail: {} }}'.format(self.data, self.code, self.detail)


class AcQuantumRawConfig:

    def __init__(self, system_config, one_q_gate_fidelities, qubit_parameter, system_status, two_q_gate_fidelity):
        self.system_config = BackendSystemConfig.from_dict(system_config)
        self.one_q_gate_fidelities = OneQGateFidelities.from_dict(one_q_gate_fidelities)
        self.qubit_parameter = QubitParameter.from_dict(qubit_parameter)
        self.system_status = SystemStatus.from_dict(system_status)
        self.two_q_gate_fidelity = TwoQGateFidelity.from_dict(two_q_gate_fidelity)

    @classmethod
    def from_json(cls, values):
        # type: ([dict]) -> AcQuantumRawConfig
        return AcQuantumRawConfig(*values)


class BackendSystemConfig:

    def __init__(self, computer_id, config_key, config_value):
        # type: (str, str, SystemConfigValue) -> None
        self.config_value = config_value  # type: SystemConfigValue
        self.config_key = config_key
        self.computer_id = computer_id

    @classmethod
    def from_dict(cls, values):
        # type: (dict) -> BackendSystemConfig
        config_value = SystemConfigValue.from_dict(json.loads(values['configValue']))
        return BackendSystemConfig(values['computerId'], values['configKey'], config_value)


class SystemConfigValue:

    def __init__(self, one_q_gates, one_q_gates_label, two_q_gates, two_q_gates_label, measure_size_upper_limit):
        # type: ([str], [str], [str], [str], int) -> None
        self.one_q_gates = one_q_gates
        self.one_q_gates_label = one_q_gates_label
        self.two_q_gates = two_q_gates
        self.two_q_gates_label = two_q_gates_label
        self.measure_size_upper_limit = measure_size_upper_limit

    @classmethod
    def from_dict(cls, values):
        # type: (dict) -> SystemConfigValue
        return SystemConfigValue(values['oneQGates'], values['oneQGatesLabel'], values['twoQGates'],
                                 values['twoQGatesLabel'], values['measureSizeUpperLimit'])


class OneQGateFidelities:

    def __init__(self, computer_id, config_key, config_value):
        self.config_value = config_value  # [dict]
        self.config_key = config_key
        self.computer_id = computer_id

    @classmethod
    def from_dict(cls, values):
        # type: (dict) -> OneQGateFidelities
        config_value = json.loads(values['configValue'])
        return OneQGateFidelities(values['computerId'], values['configKey'], config_value)


class QubitParameter:

    def __init__(self, computer_id, config_key, config_value):
        self.config_value = config_value
        self.config_key = config_key
        self.computer_id = computer_id

    @classmethod
    def from_dict(cls, values):
        # type: (dict) -> QubitParameter
        return QubitParameter(values['computerId'], values['configKey'], values['configValue'])


class SystemStatus:

    def __init__(self, computer_id, config_key, config_value):
        # type: (str, str, SystemStatusConfigValue) -> None
        self.config_value = config_value  # type: SystemStatusConfigValue
        self.config_key = config_key
        self.computer_id = computer_id

    @classmethod
    def from_dict(cls, values):
        # type: (dict) -> SystemStatus
        config_value = SystemStatusConfigValue.from_dict(json.loads(values['configValue']))
        return SystemStatus(values['computerId'], values['configKey'], config_value)


class SystemStatusConfigValue:

    def __init__(self, status, fridge_temperature, last_calibration_time):
        # type: (str, str, str) -> None
        self.last_calibration_time = last_calibration_time
        self.fridge_temperature = fridge_temperature
        self.status = status

    @classmethod
    def from_dict(cls, values):
        # type: (dict) -> SystemStatusConfigValue
        return SystemStatusConfigValue(values['status'], values['fridgeTemperature'], values['lastCalibrationTime'])


class TwoQGateFidelity:

    def __init__(self, computer_id, config_key, config_value):
        self.config_value = config_value  # type: [dict]
        self.config_key = config_key
        self.computer_id = computer_id

    @classmethod
    def from_dict(cls, values):
        # type: (dict) -> TwoQGateFidelity
        config_value = json.loads(values['configValue'])
        return TwoQGateFidelity(values['computerId'], values['configKey'], config_value)
