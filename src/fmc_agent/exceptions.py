"""Custom exceptions for FMC Agent."""

from typing import Optional


class FMCError(Exception):
    """Base exception for FMC Agent."""
    pass


class ValidationError(FMCError):
    """Raised when workbook validation fails."""
    
    def __init__(self, issues: list[str]) -> None:
        self.issues = issues
        super().__init__(f"Validation failed with {len(issues)} issues: {'; '.join(issues)}")


class OperationBuildError(FMCError):
    """Raised when operation command building fails."""
    pass


class ExecutionError(FMCError):
    """Raised when operation execution fails."""
    
    def __init__(self, operation_name: str, message: str, raw_output: Optional[str] = None) -> None:
        self.operation_name = operation_name
        self.message = message
        self.raw_output = raw_output
        super().__init__(f"Execution failed for {operation_name}: {message}")


class DependencyError(FMCError):
    """Raised when dependencies are missing (placeholder for future phases)."""
    
    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Missing dependencies: {', '.join(missing)}")