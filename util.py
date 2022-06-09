from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.messages.completion_message import CompletionMessage


def send(connection: BaseHubConnection, method: str, args: [], on_success=None, on_error=None):
    def on_received(message: CompletionMessage):
        if message.error:
            if on_error:
                on_error()
        else:
            if on_success:
                on_success(message.result)

    connection.send(method, args, on_received)
