from websocket import WebSocket, create_connection


class MyWebSocket(WebSocket):
    def recv_frame(self):
        frame = super().recv_frame()
        print('yay! I got this frame: ', frame)
        return frame


ws = create_connection("wss://split-ticket-svc.stake.decredbrasil.com:8477/watchWaitingList", class_=MyWebSocket)

