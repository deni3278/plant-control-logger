from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.messages.completion_message import CompletionMessage


def send(connection: BaseHubConnection, method: str, args: [], on_success, on_error):
    def on_received(message: CompletionMessage):
        if message.error:
            on_error()
        else:
            on_success(message.result)

    connection.send(method, args, on_received)
