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

from marshmallow.fields import String, Integer, List, DateTime, Boolean
from marshmallow.validate import Range, Length, OneOf, Equal, Regexp
from qiskit.validation import BaseModel, BaseSchema, bind_schema


class AcQuantumGateConfigSchema(BaseSchema):
    """Schema for AcQuantumGateConfig."""

    # Required properties.
    name = String(required=True)
    parameters = List(String(), required=True)
    qasm_def = String(required=True)

    # Optional properties.
    coupling_map = List(List(Integer(),
                             validate=Length(min=1)),
                        validate=Length(min=1))
    latency_map = List(List(Integer(validate=OneOf([0, 1])),
                            validate=Length(min=1)),
                       validate=Length(min=1))
    conditional = Boolean()
    description = String()


class AcQuantumBackendConfigurationSchema(BaseSchema):
    """Schema for AcQuantumBackendConfiguration."""

    # Required properties.
    backend_name = String(required=True)
    backend_version = String(required=True,
                             validate=Regexp("[0-9]+.[0-9]+.[0-9]+$"))
    n_qubits = Integer(required=True, validate=Range(min=1))
    basis_gates = List(String(), required=True,
                       validate=Length(min=1))
    # gates = Nested(AcQuantumGateConfigSchema, required=True, many=True,
    #                validate=Length(min=1))
    local = Boolean(required=True)
    simulator = Boolean(required=True)
    conditional = Boolean(required=True)
    open_pulse = Boolean(required=True, validate=Equal(False))
    memory = Boolean(required=True)
    max_shots = Integer(required=True, validate=Range(min=1))

    # Optional properties.
    max_experiments = Integer(validate=Range(min=1))
    sample_name = String()
    coupling_map = List(List(Integer(),
                             validate=Length(min=1)),
                        validate=Length(min=1))
    n_registers = Integer(validate=Range(min=1))
    register_map = List(List(Integer(validate=OneOf([0, 1])),
                             validate=Length(min=1)),
                        validate=Length(min=1))
    configurable = Boolean()
    credits_required = Boolean()
    online_date = DateTime()
    display_name = String()
    description = String()
    tags = List(String())


@bind_schema(AcQuantumBackendConfigurationSchema)
class AcQuantumBackendConfiguration(BaseModel):
    """Model for BackendConfiguration.

    Please note that this class only describes the required fields. For the
    full description of the model, please check ``AcQuantumBackendConfigurationSchema``.
    Attributes:
        backend_name (str): backend name.
        backend_version (str): backend version in the form X.Y.Z.
        n_qubits (int): number of qubits.
        basis_gates (list[str]): list of basis gates names on the backend.
        gates (GateConfig): list of basis gates on the backend.
        local (bool): backend is local or remote.
        simulator (bool): backend is a simulator.
        conditional (bool): backend supports conditional operations.
        open_pulse (bool): backend supports open pulse.
        memory (bool): backend supports memory.
        max_shots (int): maximum number of shots supported.
    """

    def __init__(self, backend_name, backend_version, n_qubits, basis_gates, gates, local, simulator, conditional,
                 open_pulse, memory, max_shots, **kwargs):
        # type: (str, str, int, [str], 'AcQuantumGateConfig', bool, bool , bool, bool, bool, int, dict) -> None

        super().__init__(**kwargs)
        self.backend_name = backend_name
        self.backend_version = backend_version
        self.n_qubits = n_qubits
        self.basis_gates = basis_gates
        self.gates = gates
        self.local = local
        self.simulator = simulator
        self.conditional = conditional
        self.open_pulse = open_pulse
        self.memory = memory
        self.max_shots = max_shots


@bind_schema(AcQuantumGateConfigSchema)
class AcQuantumGateConfig(BaseModel):
    """Model for AcQuantumGateConfig.

    Please note that this class only describes the required fields. For the
    full description of the model, please check ``AcQuantumGateConfigSchema``.

    Attributes:
        name (str): the gate name as it will be referred to in QASM.
        parameters (list[str]): variable names for the gate parameters (if any).
        qasm_def (str): definition of this gate in terms of QASM primitives U
            and CX.
    """

    def __init__(self, name, parameters, qasm_def, **kwargs):
        # type: (str, [str], str, dict) -> None
        self.name = name
        self.parameters = parameters
        self.qasm_def = qasm_def

        super().__init__(**kwargs)
