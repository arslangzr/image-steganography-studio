"""Domain exceptions for the image steganography application."""


class SteganographyError(Exception):
    """Base exception for steganography-related failures."""


class ValidationError(SteganographyError):
    """Raised when a user request is invalid."""


class CapacityError(SteganographyError):
    """Raised when the input image cannot hold the requested message."""
