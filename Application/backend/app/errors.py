from __future__ import annotations


class DomainError(Exception):
    def __init__(self, message: str, *, status_code: int = 400, code: str = "invalid_request"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class NotFound(DomainError):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=404, code="not_found")


class Forbidden(DomainError):
    def __init__(self, message: str = "Not permitted"):
        super().__init__(message, status_code=403, code="forbidden")


class Conflict(DomainError):
    def __init__(self, message: str, code: str = "conflict"):
        super().__init__(message, status_code=409, code=code)
