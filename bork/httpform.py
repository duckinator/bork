"""
Crude implementation of RFC 7578: "Returning Values from Forms: multipart/form-data"

https://datatracker.ietf.org/doc/html/rfc7578
"""

import http.client
import mimetypes
from pathlib import Path
import secrets

class Form:
    def __init__(self, parts):
        self.parts = parts

    def __bytes__(self, boundary=None):
        if boundary is None:
            boundary = secrets.token_hex(32)

        lines = []

        for part in self.parts:
            lines.append(f"--{boundary}".encode())
            lines += part._bytes_lines()
        lines.append(f"--{boundary}--".encode())
        lines.append("".encode())

        return b"\r\n".join(lines)

class FormField:
    def __init__(self, field, value):
        self.field = field
        self.value = value
        self.filename = None

    def _bytes_lines(self):
        lines = []

        disposition = f'form-data; name="{self.field}"'
        if self.filename:
            disposition += f'; filename="{self.filename}"'
        lines.append(f"Content-Disposition: {disposition}".encode())

        if self.filename:
            lines.append(f"Content-Type: {self._guess_content_type(self.filename)}".encode())
        else:
            lines.append(f"Content-Type: text/plain;charset=UTF-8".encode())

        lines.append("".encode())

        value = self.value
        if isinstance(value, str):
            value = value.encode()
        lines.append(value)
        return lines

    def __bytes__(self):
        return b"\r\n".join(self._bytes_lines())

    def _guess_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


class FormFile(FormField):
    def __init__(self, key, filename, value=None):
        if value is None:
            value = Path(filename).read_bytes()

        super().__init__(key, value)
        self.filename = filename
