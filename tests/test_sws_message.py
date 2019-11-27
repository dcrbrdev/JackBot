from unittest import TestCase

from sws.message import SessionUpdateMessage


DATA = '[{"name":"c17b1828e97bf66abd5329e7' \
       '3755173b43b98e18ebd4b84b19a016781d8cfa86",' \
       '"amounts":[1000000000,2000000000]}]\n'


class SessionUpdateMessageTestCase(TestCase):
    def test_init(self):
        msg = SessionUpdateMessage(
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            [1000000000, 2000000000]
        )
        self.assertEqual(msg.sws_name, 'test')
        self.assertEqual(msg.session_name, 'c17b1828e97bf66abd5329e73755173b43'
                                           'b98e18ebd4b84b19a016781d8cfa86')
        self.assertEqual(msg.amounts, [1000000000, 2000000000])

    def test_validate(self):
        self.assertRaises(
            TypeError,
            SessionUpdateMessage
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test'
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86'
        )

    def test_validate_svsp(self):
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            1,
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            [1000000000, 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            None,
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            [1000000000, 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            [],
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            [1000000000, 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            {},
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            [1000000000, 2000000000]
        )

    def test_validate_session_name(self):
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            1,
            [1000000000, 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            None,
            [1000000000, 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            [],
            [1000000000, 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            {},
            [1000000000, 2000000000]
        )

    def test_validate_amount(self):
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            {1000000000, 2000000000}
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            1000000000
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            "[1000000000, 2000000000]"
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            None
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            [None, 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            ["None", 2000000000]
        )
        self.assertRaises(
            TypeError,
            SessionUpdateMessage,
            'test',
            'c17b1828e97bf66abd5329e73755173b43b98e18ebd4b84b19a016781d8cfa86',
            [["None"], 2000000000]
        )

    def test_from_data(self):
        data = DATA
        msg = SessionUpdateMessage.from_data('test', data)
        self.assertEqual(msg.svsp, 'test')
        self.assertEqual(msg.session_name, 'c17b1828e97bf66abd5329e73755173b4'
                                           '3b98e18ebd4b84b19a016781d8cfa86')
        self.assertEqual(msg.amounts, [1000000000, 2000000000])
