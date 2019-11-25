import websocket

from sws import SessionUpdateMessage


class SessionWebSocket:
    def __init__(self, url):
        self.url = url
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

    @staticmethod
    def on_message(ws, message):
        print(SessionWebSocket.parse_message(ws.url, message))

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_close(ws):
        print("### closed ###")

    @staticmethod
    def parse_message(url, message):
        return SessionUpdateMessage.from_data(url, message)

    def run_forever(self):
        self.ws.run_forever()


if __name__ == "__main__":
    sws = SessionWebSocket("wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList")
    sws.run_forever()
