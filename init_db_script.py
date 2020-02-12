from mongoengine.errors import NotUniqueError

from db.subject import Subject
from db.observer import Observer
from db.ticket import Status


try:
    brasil = Subject("🇧🇷", "Decred Brasil",
                     "wss://split-ticket-svc.stake.decredbrasil"
                     ".com:8477/watchWaitingList",
                     "dcrbr1").save()
except NotUniqueError:
    brasil = Subject.objects.get(name="Decred Brasil")


try:
    voting = Subject("🇺🇸", "Decred Voting",
                     "wss://matcher.decredvoting.com:8477/"
                     "watchWaitingList",
                     "decredvoting1").save()
except NotUniqueError:
    voting = Subject.objects.get(name="Decred Voting")


try:
    split = Subject("🏴‍☠️", "99split",
                    "wss://split.99split.com:8477/"
                    "watchWaitingList",
                    "99split").save()
except NotUniqueError:
    split = Subject.objects.get(name="99split")


try:
    channel = Observer("@ticketsplitting", "@ticketsplitting").save()
except NotUniqueError:
    channel = Observer.objects.get(chat_id="@ticketsplitting")


try:
    immature = Status('immature').save()
except NotUniqueError:
    immature = Status.objects.get(name='immature')

try:
    live = Status('live').save()
except NotUniqueError:
    live = Status.objects.get(name='live')

try:
    voted = Status('voted').save()
except NotUniqueError:
    voted = Status.objects.get(name='voted')
