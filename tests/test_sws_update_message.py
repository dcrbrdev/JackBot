from unittest import TestCase

from sws.message import UpdateMessage, SessionData, Amount


DATA = '[{"name":"c17b1828e97bf66abd5329e7' \
       '3755173b43b98e18ebd4b84b19a016781d8cfa86",' \
       '"amounts":[1000000000,2000000000]}]\n'


class UpdateMessageTestCase(TestCase):
    def test_init(self):
        instance = UpdateMessage('test')
        self.assertEqual(instance.sws_name, 'test')
        self.assertIsInstance(instance, UpdateMessage)

    def test_validate(self):
        UpdateMessage('test')
        self.assertRaises(TypeError, UpdateMessage, 1)
        self.assertRaises(TypeError, UpdateMessage, None)
        self.assertRaises(TypeError, UpdateMessage, [])
        self.assertRaises(TypeError, UpdateMessage, {})

    def test_add_data(self):
        instance = UpdateMessage('test')
        self.assertEqual(len(instance._data), 0)

        instance.add_data(SessionData('session test', [1000000000, 200000000]))
        self.assertEqual(len(instance._data), 1)

    def test_add_data_error(self):
        instance = UpdateMessage('test')
        self.assertEqual(len(instance._data), 0)

        self.assertRaises(TypeError, instance.add_data, '')
        self.assertRaises(TypeError, instance.add_data, 1)
        self.assertRaises(TypeError, instance.add_data, [])
        self.assertRaises(TypeError, instance.add_data, {})
        self.assertRaises(TypeError, instance.add_data, None)
        self.assertEqual(len(instance._data), 0)

    def test_from_msg(self):
        msg = DATA
        instance = UpdateMessage.from_msg('test', msg)
        self.assertEqual(instance.sws_name, 'test')
        self.assertEqual(len(instance._data), 1)
        self.assertIsInstance(instance._data[0], SessionData)

        session_data = instance._data[0]
        self.assertEqual(session_data.session_name,
                         'c17b1828e97bf66abd5329e737551'
                         '73b43b98e18ebd4b84b19a016781d8cfa86')
        self.assertEqual(len(session_data.amounts), 2)
        self.assertIsInstance(session_data.amounts[0], Amount)
        self.assertIsInstance(session_data.amounts[1], Amount)
        self.assertEqual(session_data.amounts[0].value, 10.0)
        self.assertEqual(session_data.amounts[1].value, 20.0)
