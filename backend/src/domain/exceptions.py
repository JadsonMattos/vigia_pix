"""Domain exceptions"""


class DomainException(Exception):
    """Base domain exception"""
    pass


class LegislationNotFoundError(DomainException):
    """Legislation not found"""
    pass


class AIServiceError(DomainException):
    """AI service error"""
    pass


class CitizenNotFoundError(DomainException):
    """Citizen not found"""
    pass


class AlertNotFoundError(DomainException):
    """Alert not found"""
    pass




