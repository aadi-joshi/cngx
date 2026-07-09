"""Custom exceptions for cngx."""


class CngxError(Exception):
    """Base exception for all cngx errors."""

    pass


# ---- Client errors ----


class ClientError(CngxError):
    """Base for errors caused by client input or configuration."""

    pass


class ContractError(ClientError):
    """Raised when a contract is invalid or cannot be loaded."""

    pass


class ValidationError(ClientError):
    """Raised when input validation fails."""

    pass


# ---- Storage / lookup errors ----


class TraceNotFoundError(CngxError):
    """Raised when a reasoning trace cannot be found."""

    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        super().__init__(f"Trace not found: {trace_id}")


class BaselineNotFoundError(CngxError):
    """Raised when a baseline cannot be found."""

    def __init__(self, baseline_name: str):
        self.baseline_name = baseline_name
        super().__init__(f"Baseline not found: {baseline_name}")


class StorageError(CngxError):
    """Raised when a storage operation fails."""

    pass


# ---- Capture / adapter errors ----


class CaptureError(CngxError):
    """Raised when trace capture fails."""

    pass


class AdapterError(CngxError):
    """Raised when an LLM adapter fails."""

    pass


# ---- Analysis errors ----


class FingerprintError(CngxError):
    """Raised when fingerprint extraction fails."""

    pass


class DiffError(CngxError):
    """Raised when diff computation fails."""

    pass


class DriftError(CngxError):
    """Raised when drift detection fails."""

    pass


class EvalError(CngxError):
    """Raised when evaluation fails."""

    pass


# ---- Configuration errors ----


class ConfigError(CngxError):
    """Raised when configuration is invalid."""

    pass


# ---- Cloud / auth errors ----


class AuthenticationError(CngxError):
    """Raised when API key authentication fails."""

    pass


class RateLimitError(CngxError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s.")


class SecurityError(CngxError):
    """Raised for security-related failures (regex, input sanitization, etc.)."""

    pass
