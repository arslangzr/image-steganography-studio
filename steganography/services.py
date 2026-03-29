"""Core services for image steganography."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from PIL import Image

from .exceptions import CapacityError, ValidationError
from .models import EncodeRequest


@dataclass
class PillowImageRepository:
    """Handles image persistence using Pillow."""

    def open_rgb_image(self, image_path: str) -> Image.Image:
        path = Path(image_path)
        if not path.exists():
            raise ValidationError(f"Image not found: {image_path}")

        with Image.open(path, "r") as image:
            return image.convert("RGB")

    def save_image(self, image: Image.Image, output_path: str) -> None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output)


@dataclass
class MessageValidator:
    """Validates encode requests before processing."""

    safe_extensions: tuple[str, ...] = (".png", ".bmp", ".tiff")

    def validate_encode_request(self, request: EncodeRequest, capacity: int) -> None:
        if not request.source_image_path.strip():
            raise ValidationError("Please choose a source image.")
        if not request.output_image_path.strip():
            raise ValidationError("Please choose where to save the encoded image.")
        if not request.message:
            raise ValidationError("Please enter a message to hide.")
        if len(request.message) > capacity:
            raise CapacityError(
                f"Message is too long for this image. Capacity: {capacity} characters."
            )

    def build_output_warning(self, output_path: str) -> str | None:
        suffix = Path(output_path).suffix.lower()
        if suffix and suffix not in self.safe_extensions:
            return (
                "Lossy image formats may destroy hidden data. "
                "Use PNG, BMP, or TIFF for best results."
            )
        return None


class LSBSteganographyCodec:
    """Encodes and decodes messages with least significant bit steganography."""

    @staticmethod
    def _text_to_binary_chunks(message: str) -> list[str]:
        return [format(ord(character), "08b") for character in message]

    @staticmethod
    def capacity_for_image(image: Image.Image) -> int:
        pixel_count = image.size[0] * image.size[1]
        return pixel_count // 3

    def _iter_modified_pixels(
        self,
        pixels: Sequence[tuple[int, int, int]] | Iterable[tuple[int, int, int]],
        message: str,
    ) -> Iterator[tuple[int, int, int]]:
        binary_chunks = self._text_to_binary_chunks(message)
        pixel_iterator = iter(pixels)

        for index, chunk in enumerate(binary_chunks):
            block = [
                value
                for value in next(pixel_iterator)[:3]
                + next(pixel_iterator)[:3]
                + next(pixel_iterator)[:3]
            ]

            for bit_index, bit in enumerate(chunk):
                if bit == "0" and block[bit_index] % 2 != 0:
                    block[bit_index] -= 1
                elif bit == "1" and block[bit_index] % 2 == 0:
                    block[bit_index] = block[bit_index] - 1 if block[bit_index] != 0 else 1

            if index == len(binary_chunks) - 1:
                block[-1] |= 1
            else:
                block[-1] &= ~1

            yield tuple(block[:3])
            yield tuple(block[3:6])
            yield tuple(block[6:9])

    def encode(self, image: Image.Image, message: str) -> Image.Image:
        encoded = image.copy()
        width = encoded.size[0]
        x_position, y_position = 0, 0

        for pixel in self._iter_modified_pixels(list(encoded.getdata()), message):
            encoded.putpixel((x_position, y_position), pixel)
            x_position += 1
            if x_position == width:
                x_position = 0
                y_position += 1

        return encoded

    def decode(self, image: Image.Image) -> str:
        pixel_iterator = iter(image.getdata())
        decoded_message = ""

        while True:
            block = [
                value
                for value in next(pixel_iterator)[:3]
                + next(pixel_iterator)[:3]
                + next(pixel_iterator)[:3]
            ]
            binary_string = "".join("1" if value % 2 else "0" for value in block[:8])
            decoded_message += chr(int(binary_string, 2))

            if block[-1] % 2 != 0:
                return decoded_message


@dataclass
class SteganographyService:
    """Coordinates validation, encoding, decoding, and persistence."""

    repository: PillowImageRepository
    validator: MessageValidator
    codec: LSBSteganographyCodec

    def get_capacity(self, image_path: str) -> int:
        image = self.repository.open_rgb_image(image_path)
        return self.codec.capacity_for_image(image)

    def encode_message(self, request: EncodeRequest) -> str | None:
        source_image = self.repository.open_rgb_image(request.source_image_path)
        capacity = self.codec.capacity_for_image(source_image)
        self.validator.validate_encode_request(request, capacity)

        encoded_image = self.codec.encode(source_image, request.message)
        self.repository.save_image(encoded_image, request.output_image_path)
        return self.validator.build_output_warning(request.output_image_path)

    def decode_message(self, image_path: str) -> str:
        if not image_path.strip():
            raise ValidationError("Please choose an image to decode.")

        image = self.repository.open_rgb_image(image_path)
        return self.codec.decode(image)


def build_default_service() -> SteganographyService:
    """Creates the default dependency graph for the application."""

    return SteganographyService(
        repository=PillowImageRepository(),
        validator=MessageValidator(),
        codec=LSBSteganographyCodec(),
    )
