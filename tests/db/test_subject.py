from unittest import TestCase

import pytest
from mongoengine.errors import NotUniqueError

from tests.fixtures import mongo  # noqa F401
from db.subscription import Subject


@pytest.mark.usefixtures('mongo')
class SubjectTestCase(TestCase):
    def test_create(self):
        Subject(emoji="🇧🇷", name="Decred Brasil",
                url="wss://split-ticket-svc.stake.decredbrasil"
                    ".com:8477/watchWaitingList").save()
        self.assertEqual(Subject.objects.count(), 1)
        sub: Subject = Subject.objects.first()
        self.assertEqual(sub.emoji, "🇧🇷")
        self.assertEqual(sub.name, "Decred Brasil")
        self.assertEqual(sub.url, "wss://split-ticket-svc.stake."
                                  "decredbrasil.com:8477/watchWaitingList")

    def test_header(self):
        Subject(emoji="🇧🇷", name="Decred Brasil",
                url="wss://split-ticket-svc.stake.decredbrasil"
                    ".com:8477/watchWaitingList").save()
        sub: Subject = Subject.objects.first()
        self.assertEqual(sub.header, "🇧🇷 Decred Brasil")

    def test_str(self):
        Subject(emoji="🇧🇷", name="Decred Brasil",
                url="wss://split-ticket-svc.stake.decredbrasil"
                    ".com:8477/watchWaitingList").save()
        sub: Subject = Subject.objects.first()
        self.assertEqual(sub.__str__(),
                         "🇧🇷 Decred Brasil wss://split-ticket-svc.stake"
                         ".decredbrasil.com:8477/watchWaitingList")

    def test_unique_url(self):
        Subject(emoji="🇧", name="Decred Brasil",
                url="wss://split-ticket-svc.stake.decredbrasil"
                    ".com:8477/watchWaitingList").save()
        self.assertEqual(Subject.objects.count(), 1)

        sub_2 = Subject(emoji="🇧🇷", name="ASDDecred Brasil",
                        url="wss://split-ticket-svc.stake.decredbrasil"
                            ".com:8477/watchWaitingList")
        self.assertRaises(NotUniqueError, sub_2.save)
        self.assertEqual(Subject.objects.count(), 1)

    def test_unique_header(self):
        Subject(emoji="🇧🇷", name="Decred Brasil",
                url="wss://split-ticket-svc.stake.decredbrasil"
                    ".com:8477/watchWaitingList").save()
        self.assertEqual(Subject.objects.count(), 1)

        sub_2 = Subject(emoji="🇧🇷", name="Decred Brasil",
                        url="wss://asdasdtbrasil.com:8477/watchWaitingList")
        self.assertRaises(NotUniqueError, sub_2.save)
        self.assertEqual(Subject.objects.count(), 1)
