from .datac import QmtDataClient


class OmegaQMT:
    _client = None

    @classmethod
    def init(cls, port: int = 58610, reconnect_port=None, enable_hello: bool = False, auto_connect: bool = True):
        cls._client = QmtDataClient(
            port=port,
            reconnect_port=reconnect_port,
            enable_hello=enable_hello,
            auto_connect=auto_connect,
        )

    @property
    def data(self) -> QmtDataClient:
        if self._client is None:
            self.init()
        return self._client


api = OmegaQMT()

