class QmtError(Exception):
    pass


class QmtNotInstalledError(QmtError):
    pass


class QmtConnectionError(QmtError):
    pass

