"""
Comprehensive error handling and logging for the Automation Agent system
"""
import asyncio
import traceback
from typing import Any, Dict, Optional, Callable
from functools import wraps
from loguru import logger
from datetime import datetime
from pathlib import Path

class AutomationError(Exception):
    """Base exception for automation-related errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "AUTOMATION_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()

class ValidationError(AutomationError):
    """Error raised during configuration validation"""
    def __init__(self, message: str, validation_errors: list = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.validation_errors = validation_errors or []

class MCPConnectionError(AutomationError):
    """Error raised when MCP server connection fails"""
    def __init__(self, message: str):
        super().__init__(message, "MCP_CONNECTION_ERROR")

class ScriptGenerationError(AutomationError):
    """Error raised during script generation"""
    def __init__(self, message: str, automation_type: str = None):
        super().__init__(message, "SCRIPT_GENERATION_ERROR")
        self.automation_type = automation_type

class DeploymentError(AutomationError):
    """Error raised during script deployment"""
    def __init__(self, message: str, script_path: str = None):
        super().__init__(message, "DEPLOYMENT_ERROR")
        self.script_path = script_path

class GoogleSheetsError(AutomationError):
    """Error raised during Google Sheets operations"""
    def __init__(self, message: str, sheet_id: str = None):
        super().__init__(message, "GOOGLE_SHEETS_ERROR")
        self.sheet_id = sheet_id

class ErrorHandler:
    """Centralized error handling and logging"""

    def __init__(self, log_path: str = "/tmp/logs/automation_errors.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_counts = {}

    def log_error(
        self,
        error: Exception,
        context: str = "",
        automation_name: str = "",
        row_number: int = None,
        additional_info: Dict[str, Any] = None
    ):
        """Log error with context and additional information"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "automation_name": automation_name,
            "row_number": row_number,
            "traceback": traceback.format_exc(),
            "additional_info": additional_info or {}
        }

        # Log to console
        logger.error(f"[{context}] {error_info['error_type']}: {error_info['error_message']}")

        # Log detailed info to file
        with open(self.log_path, 'a') as f:
            f.write(f"{error_info}\n")

        # Update error counts
        error_key = f"{error_info['error_type']}:{context}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        return error_info

    def handle_automation_error(
        self,
        error: Exception,
        automation_name: str = "",
        row_number: int = None,
        context: str = "automation_processing"
    ) -> Dict[str, Any]:
        """Handle automation-specific errors"""
        error_response = {
            "success": False,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat()
        }

        if isinstance(error, AutomationError):
            error_response.update({
                "error_code": error.error_code,
                "details": error.details
            })

        self.log_error(error, context, automation_name, row_number)
        return error_response

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": dict(self.error_counts),
            "top_errors": sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

def with_error_handling(
    context: str = "",
    return_on_error: Any = None,
    re_raise: bool = False,
    log_handler: ErrorHandler = None
):
    """Decorator for adding error handling to functions"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_handler:
                    log_handler.handle_automation_error(e, context=context or func.__name__)
                else:
                    logger.error(f"Error in {func.__name__}: {e}")

                if re_raise:
                    raise
                return return_on_error

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_handler:
                    log_handler.handle_automation_error(e, context=context or func.__name__)
                else:
                    logger.error(f"Error in {func.__name__}: {e}")

                if re_raise:
                    raise
                return return_on_error

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def validate_automation_config(config: Dict[str, Any], automation_type: str) -> None:
    """Validate automation configuration and raise ValidationError if invalid"""
    errors = []

    if not isinstance(config, dict):
        raise ValidationError("Configuration must be a dictionary")

    if "type" not in config:
        errors.append("Missing required field: type")
    elif config["type"] != automation_type:
        errors.append(f"Configuration type '{config['type']}' does not match automation type '{automation_type}'")

    # Type-specific validation
    if automation_type == "file_processor":
        if "source_directory" not in config:
            errors.append("file_processor requires 'source_directory'")
        if "actions" not in config:
            errors.append("file_processor requires 'actions'")

    elif automation_type == "api_monitor":
        if "endpoint" not in config:
            errors.append("api_monitor requires 'endpoint'")

    elif automation_type == "data_sync":
        if "source" not in config:
            errors.append("data_sync requires 'source'")
        if "destination" not in config:
            errors.append("data_sync requires 'destination'")

    elif automation_type == "notification_sender":
        if "trigger_conditions" not in config:
            errors.append("notification_sender requires 'trigger_conditions'")
        if "notification_channels" not in config:
            errors.append("notification_sender requires 'notification_channels'")

    elif automation_type == "report_generator":
        if "report_type" not in config:
            errors.append("report_generator requires 'report_type'")

    if errors:
        raise ValidationError(f"Configuration validation failed for {automation_type}", errors)

class RetryHandler:
    """Handle retries with exponential backoff"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        context: str = "",
        **kwargs
    ) -> Any:
        """Retry function with exponential backoff"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if attempt == self.max_retries:
                    logger.error(f"All {self.max_retries} retry attempts failed for {context}: {e}")
                    break

                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.warning(f"Attempt {attempt + 1} failed for {context}: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)

        raise last_exception

class CircuitBreaker:
    """Circuit breaker pattern for handling failures"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function through circuit breaker"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise AutomationError("Circuit breaker is OPEN")

        try:
            if asyncio.iscoroutinefunction(func):
                result = asyncio.create_task(func(*args, **kwargs))
            else:
                result = func(*args, **kwargs)

            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset"""
        return (
            self.last_failure_time and
            datetime.now().timestamp() - self.last_failure_time > self.recovery_timeout
        )

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now().timestamp()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

# Global error handler instance
error_handler = ErrorHandler()

# Global retry handler instance
retry_handler = RetryHandler()

# Global circuit breaker for external services
external_service_breaker = CircuitBreaker()