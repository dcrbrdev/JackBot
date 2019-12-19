from unittest import TestCase

import pytest

from tests.fixtures import mongo  # noqa F401
from db.update_message import Session, Amount

DATA = {
    "name": "c17b1828e97bf66abd5329e7",
    "amounts": [1000000000, 2000000000]
}


@pytest.mark.usefixtures('mongo')
class SessionTestCase(TestCase):
    def test_init(self):
        instance = Session(hash='test',
                           amounts=[Amount(1000000000), Amount(2000000000)])
        self.assertEqual(instance.hash, 'test')
        self.assertEqual(len(instance.amounts), 2)
        self.assertIsInstance(instance.amounts[0], Amount)
        self.assertIsInstance(instance.amounts[1], Amount)
        self.assertEqual(instance.amounts[0].value, 10.0)
        self.assertEqual(instance.amounts[1].value, 20.0)

    def test_equal(self):
        instance = Session(hash='test',
                           amounts=[Amount(1000000000), Amount(2000000000)])
        other = Session(hash='test',
                        amounts=[Amount(1000000000), Amount(2000000000)])
        self.assertTrue(instance.equal(other))

    def test_equal_false(self):
        instance = Session(hash='test',
                           amounts=[Amount(1000000000), Amount(2000000000)])
        other = Session(hash='test',
                        amounts=[Amount(1000000000), Amount(2500000000)])
        self.assertFalse(instance.equal(other))

    def test_str(self):
        instance = Session(hash='test',
                           amounts=[Amount(1000000000), Amount(2000000000)])
        self.assertEqual(instance.__str__(),
                         f"{instance.hash}:\t[10.0 DCR, 20.0 DCR]"
                         f"\nTotal: 30.0 DCR")

    def test_from_data(self):
        instance = Session.from_data(DATA)
        self.assertEqual(instance.hash, 'c17b1828e97bf66abd5329e7')
        self.assertEqual(len(instance.amounts), 2)
        self.assertIsInstance(instance.amounts[0], Amount)
        self.assertIsInstance(instance.amounts[1], Amount)
        self.assertEqual(instance.amounts[0].value, 10.0)
        self.assertEqual(instance.amounts[1].value, 20.0)
