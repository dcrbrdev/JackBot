from unittest import TestCase

from sws.message import SessionData, Amount


class SessionDataTestCase(TestCase):
    def test_init(self):
        instance = SessionData(session_name='test',
                               amounts=[1000000000, 2000000000])
        self.assertEqual(instance.session_name, 'test')
        self.assertEqual(len(instance.amounts), 2)
        self.assertIsInstance(instance.amounts[0], Amount)
        self.assertIsInstance(instance.amounts[1], Amount)
        self.assertEqual(instance.amounts[0].value, 10.0)
        self.assertEqual(instance.amounts[1].value, 20.0)

    def test_validate(self):
        SessionData(session_name='test', amounts=[1000000000, 2000000000])
        self.assertRaises(TypeError, SessionData,
                          session_name=1, amounts=[])
        self.assertRaises(TypeError, SessionData,
                          session_name=None, amounts=[])
        self.assertRaises(TypeError, SessionData,
                          session_name=[], amounts=[])
        self.assertRaises(TypeError, SessionData,
                          session_name={}, amounts=[])

        self.assertRaises(TypeError, SessionData,
                          session_name='test', amounts={'1': 1})
        self.assertRaises(TypeError, SessionData,
                          session_name='test', amounts="1")
        self.assertRaises(TypeError, SessionData,
                          session_name='test', amounts=None)
        self.assertRaises(TypeError, SessionData,
                          session_name='test', amounts=1)

    def test_str(self):
        instance = SessionData(session_name='test',
                               amounts=[1000000000, 2000000000])
        self.assertEqual(instance.__str__(),
                         f"{instance.session_name}:\t[10.0 DCR, 20.0 DCR]"
                         f"\nTotal: 30.0 DCR")
