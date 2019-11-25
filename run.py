from bot import JackBot
from sws import SessionWebSocket


if __name__ == '__main__':
    JackBot.instance()
    SessionWebSocket("Decred Brasil",
                     "wss://split-ticket-svc.stake."
                     "decredbrasil.com:8477/watchWaitingList")
    SessionWebSocket("Decred Voting",
                     "wss://matcher.decredvoting.com:8477/watchWaitingList")
    SessionWebSocket.start_all()
    SessionWebSocket.join_all()
