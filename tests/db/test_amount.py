from unittest import TestCase

import pytest

from tests.fixtures import mongo  # noqa F401
from db.update_message import Amount


@pytest.mark.usefixtures('mongo')
class AmountTestCase(TestCase):
    def test_init(self):
        instance = Amount(2000000000)
        self.assertEqual(instance._value, 2000000000)
        self.assertIsInstance(instance, Amount)

    def test_value_get(self):
        instance = Amount(2000000000)
        self.assertEqual(instance._value, 2000000000)
        self.assertEqual(instance.value, 20)

    def test_value_set(self):
        instance = Amount(2000000000)
        self.assertEqual(instance._value, 2000000000)

        instance.value = 3000000000
        self.assertEqual(instance._value, 3000000000)
        self.assertEqual(instance.value, 30)

    def test_value_set_validate(self):
        instance = Amount(2000000000)
        self.assertEqual(instance._value, 2000000000)

        self.assertRaises(TypeError, setattr, instance.value, '3000000000')
        self.assertRaises(TypeError, setattr, instance.value, [3000000000])
        self.assertRaises(TypeError, setattr, instance.value, 3000000000.0)
        self.assertRaises(TypeError, setattr, instance.value, {3000000000.0})

    def test_value_str(self):
        instance = Amount(2000000000)
        self.assertEqual(instance.__str__(), '20.0 DCR')
