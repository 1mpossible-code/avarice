from database import get_products


class Catalog:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.current_prod = 0
        self.products = get_products()
        self.prod_amount = len(self.products) - 1
