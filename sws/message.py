from json import loads


class SessionUpdateMessage:
    def __init__(self, svsp, session_name, amounts):
        self.svsp = svsp
        self.session_name = session_name
        self.amounts = amounts
        self.validate()

    def __str__(self):
        return f'{self.svsp} {self.session_name} {self.amounts}'

    def validate(self):
        if not isinstance(self.svsp, str):
            raise TypeError(f'Svsp value {self.svsp} is not a valid string')
        if not isinstance(self.session_name, str):
            raise TypeError(f'Session Name value '
                            f'{self.session_name} is not a valid string')
        if not isinstance(self.amounts, list):
            raise TypeError(f'Amounts value {self.amounts} is not a list')
        else:
            for amount in self.amounts:
                if not isinstance(amount, int):
                    raise TypeError(f'Amount value {amount} is not a int')

    @classmethod
    def from_data(cls, svsp, data):
        json_data = loads(data)
        msgs = []
        for _data in json_data:
            msgs.append(
                cls(svsp=svsp,
                    session_name=_data.get('name'),
                    amounts=_data.get('amounts'))
            )
        return msgs[0] if len(msgs) == 1 else msgs
