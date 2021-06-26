class Share:
    def __init__(self, dic):
        self.dic = dic

    def get_names(self):
        result = []
        for stock in self.dic:
            result

    def get_amount(self):
        return self.amount

    def set_amount(self, amount):
        self.amount += amount

    def to_dict(self):
        return (
            f'{self.name}',
            f'{self.amount}'
        )
