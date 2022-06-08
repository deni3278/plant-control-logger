from threading import Lock

from signalrcore.hub.base_hub_connection import BaseHubConnection


def send(connection: BaseHubConnection, method: str, args: [], on_success, on_error, timeout: int = 2):
    lock: Lock = Lock()
    lock.acquire()

    connection.send(method, args, lambda m: lock.release())

    if not lock.acquire(timeout=timeout):
        on_error()
    else:
        on_success()
