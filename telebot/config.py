from dotenv import load_dotenv
import os


load_dotenv()

TOKEN = os.getenv("BOT_API")


class APIData:

    def __init__(self, bank=None, currency=None, date=None):
        self.bank = bank
        self.currency = currency
        self.date = date
