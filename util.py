from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.messages.completion_message import CompletionMessage


def send(connection: BaseHubConnection, method: str, args: [], on_success, on_error):
    def callback(message: CompletionMessage):
        if message.error:
            on_error()
        else:
            on_success(message.result)

    connection.send(method, args, callback)
