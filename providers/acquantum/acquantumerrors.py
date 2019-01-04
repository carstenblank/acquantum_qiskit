from qiskit.qiskiterror import QISKitError


class AcQuantumError(QISKitError):
    def __init__(self, *message):
        """Set the error message."""
        super().__init__(' '.join(message))
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)


class AcQuantumAccountError(AcQuantumError):
    """Base class for errors raised by account management."""

    def __init__(self, *message):
        super().__init__(*message)
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)


class AcQuantumJobError(AcQuantumError):
    """Base class for errors raised by job errors"""

    def __init__(self, *message):
        super().__init__(*message)
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)


class AcQuantumJobTimeOutError(AcQuantumJobError):

    def __init__(self, *message):
        super().__init__(*message)
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)


class AcQuantumBackendError(AcQuantumError):

    def __init__(self, *message):
        super().__init__(*message)
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)
