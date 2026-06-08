"""This module is a factory for creating mock APIResponse objects."""


class MockAPIResponse:
    """Class that mocks API responses"""

    def __init__(
        self,
        endpoint: str = "",
        json: dict | None = None,
        status: int = 200,
        status_text: str = "OK",
        body: bytes = b"",  # bytes obj with 0 length
        ok: bool = True,
        text: str = "",
    ):

        self._endpoint = endpoint
        self._json = json
        self._status = status
        self._status_text = status_text
        self._body = body
        self._ok = ok
        self._text = text

    @property
    def endpoint(self):
        """Returns endpoint."""
        return self._endpoint

    @property
    def ok(self) -> bool:
        """Returns bool just like response.ok"""
        return self._ok

    @property
    def status(self) -> int:
        """Returns status as int"""
        return self._status

    @property
    def status_text(self) -> str:
        """Returns status text as str"""
        return self._status_text

    def json(self) -> dict | None:
        """Returns json response."""
        # we don't use @property because
        #  we want to simulate the actual ()
        return self._json

    def body(self) -> bytes:
        """Returns body as bytes"""
        return self._body

    def text(self) -> str:
        """Returns text as str"""
        return self._text
