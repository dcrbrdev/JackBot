import logging
from threading import Thread
from time import sleep

from utils.dcrdata import request_dcr_data
from bot.jack import JackBot
from db.ticket import Ticket


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

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

            logger.info(f"Getting latest block...")
            data = request_dcr_data('block/best')
            new_block = data.get('height')
            logger.info(f"Latest block is {new_block}!")

            logger.info(f"Getting all voted tickets...")
            voted_tickets = Ticket.voted()
            logger.debug(f"Voted tickets: {tickets}")
            for ticket in voted_tickets:
                logger.debug(f"Checking if ticket {ticket} is expendable...")
                ticket.change_spendable(new_block)

            logger.info(f"Deleting all voted expendable tickets...")
            logger.info(f"Deleting {Ticket.voted_and_expendable()}...")
            Ticket.voted_and_expendable().delete()

            logger.info(f"Sleeping for 1 hour...")
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
