from unittest import TestCase, mock

from ws import SessionWebSocket


DATA = '[{"name":"c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86",' \
       '"amounts":[1000000000,2000000000]}]\n'
URL = "ws://echo.websocket.org/"


class SessionWebSocketTest(TestCase):
    def test_parse_message(self):
        msg = DATA
        parsed_expect = [
            {
                "name": "c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86",
                "amounts": [1000000000, 2000000000]
            }
        ]

        parsed_msg = SessionWebSocket.parse_message(msg)

        self.assertEqual(parsed_expect, parsed_msg)
