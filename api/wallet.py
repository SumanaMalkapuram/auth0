from copy import copy


class _Wallet(object):
    
    def __init__(self):
        self.wallet = {}

    def has_card(self, card_id):
        return card_id in self.wallet

    def add_card(self, card_id, balance):
        if card_id in self.wallet:
            raise Exception('duplicate:card')

        if balance < 0:
            raise Exception('invalid:balance')

        self.wallet[card_id] = balance

    def remove_card(self, card_id):
        if self.has_card(card_id):
            self.wallet.pop(card_id)

    def modify_balance(self, card_id, amount):
        if self.has_card(card_id):
            new_amount = self.wallet[card_id] + amount
            if new_amount > 0:
                self.wallet[card_id] = new_amount
                return

        raise Exception({'code': 'invalid:card', 'description': 'Invalid action'}, 401)

    def get_balance(self, card_id):
        if self.has_card(card_id):
            return self.wallet[card_id]

        raise Exception("invalid:card")

    def get_wallet(self):
        return copy(self.wallet)


Wallet = _Wallet()
Wallet.add_card(1, 200)
Wallet.add_card(3, 200)
Wallet.add_card(5, 200)
