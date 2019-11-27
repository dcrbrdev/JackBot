from unittest import TestCase

from sws.message import Amount


class AmountTestCase(TestCase):
    def test_init(self):
        amount = Amount(2000000000)
        self.assertEqual(amount._value, 2000000000)
        self.assertIsInstance(amount, Amount)

    def test_value_get(self):
        amount = Amount(2000000000)
        self.assertEqual(amount._value, 2000000000)
        self.assertEqual(amount.value, 20)

    def test_value_set(self):
        amount = Amount(2000000000)
        self.assertEqual(amount._value, 2000000000)

        amount.value = 3000000000
        self.assertEqual(amount._value, 3000000000)
        self.assertEqual(amount.value, 30)

    def test_value_set_validate(self):
        amount = Amount(2000000000)
        self.assertEqual(amount._value, 2000000000)

        self.assertRaises(TypeError, setattr, amount.value, '3000000000')
        self.assertRaises(TypeError, setattr, amount.value, [3000000000])
        self.assertRaises(TypeError, setattr, amount.value, 3000000000.0)
        self.assertRaises(TypeError, setattr, amount.value, {3000000000.0})

    def test_value_str(self):
        amount = Amount(2000000000)
        self.assertEqual(amount.__str__(), '20.0 DCR')
