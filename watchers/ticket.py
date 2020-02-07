import logging
from threading import Thread
from time import sleep

from bot.jack import JackBot
from db.ticket import Ticket, Status


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


class TicketWatcher(Thread):
    def run(self):
        while True:
            logger.info(f"Getting all tickets...")
            tickets = Ticket.objects.all()
            logger.debug(f"Tickets: {tickets}")
            for ticket in tickets:
                logger.debug(f"Fetching ticket {ticket}")
                ticket.fetch()

            logger.info(f"Deleting all voted tickets...")
            Ticket.objects.filter(_status=Status.voted()).delete()

            logger.info(f"Sleeping for 1 minute...")
            sleep(60)


if __name__ == "__main__":
    JackBot.instance()
    logger.info("Creating ticket watcher...")
    tw = TicketWatcher()
    logger.info(f"Ticket watcher created: {tw}")
    logger.info("Starting all ticket watcher...")
    tw.start()
    logger.info("Joining ticket watcher...")
    tw.join()
