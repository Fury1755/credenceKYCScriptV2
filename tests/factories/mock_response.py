'''This module is a factory for creating mock APIResponse objects'''

class MockAPIResponse:
    '''Class that mocks API responses'''

    def __init__(self,
                 endpoint: str = "",
                 json: dict | None = None,
                 status: int = 200,
                 status_text: str = "OK",
                 body: bytes = b"",  # bytes obj with 0 length
                 ok: bool = True):


        self._endpoint = endpoint
        self._json = json
        self._status = status
        self._status_text = status_text
        self._body = body
        self._ok = ok

    @property
    def endpoint(self):
        '''Returns endpoint.'''
        return self._endpoint

    @property
    def ok(self):
        '''Returns bool just like response.ok'''
        return self._ok

    def json(self):
        '''Returns json response.'''
        # we don't use @property because
        #  we want to simulate the actual ()
        return self._json

    def status(self):
        '''Returns status as int'''
        return self._status

    def status_text(self):
        '''Returns status text as str'''
        return self._status_text

    def body(self):
        '''Returns body as bytes'''
        return self._body
