from mongoengine.errors import NotUniqueError

from db.subject import Subject
from db.observer import Observer
from db.exceptions import ObserverAlreadyRegisteredError


try:
    brasil = Subject("🇧🇷", "Decred Brasil",
                     "wss://split-ticket-svc.stake.decredbrasil"
                     ".com:8477/watchWaitingList").save()
except NotUniqueError:
    brasil = Subject.objects.get(name="Decred Brasil")


try:
    voting = Subject("🇺🇸", "Decred Voting",
                     "wss://matcher.decredvoting.com:8477/"
                     "watchWaitingList").save()
except NotUniqueError:
    voting = Subject.objects.get(name="Decred Voting")


try:
    channel = Observer("@ticketsplitting", "@ticketsplitting").save()
except NotUniqueError:
    channel = Observer.objects.get(chat_id="@ticketsplitting")
