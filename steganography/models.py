"""Data models used by the application."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EncodeRequest:
    """Represents an encoding request from the user interface."""

    source_image_path: str
    output_image_path: str
    message: str


@dataclass(frozen=True)
class EncodeResult:
    """Represents the result of a successful encode operation."""

    output_image_path: str
    warning: str | None = None
