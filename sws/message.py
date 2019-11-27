from json import loads


class Amount:
    ATOM_DECIMALS = 100000000

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"{self.value} DCR"

    @property
    def value(self):
        return self._value/self.ATOM_DECIMALS

    @value.setter
    def value(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"{value} {type(value)} não é inteiro")
        self._value = value


class SessionMessage:
    def __init__(self, session_name, amounts):
        self.session_name = session_name
        self.amounts = []
        for value in amounts:
            self.amounts.append(Amount(value))
        self.validate()

    def __str__(self):
        string = f"{self.session_name[:32]}:\t["
        total = 0
        for index, amount in enumerate(self.amounts):
            total += amount.value
            string += f"{amount}"
            string += ", " if index != len(self.amounts)-1 else "]"
        string += f"\nTotal: {total} DCR"
        return string

    def validate(self):
        if not isinstance(self.session_name, str):
            raise TypeError(f"Session Name value "
                            f"{self.session_name} is not a valid string")
        if not isinstance(self.amounts, list):
            raise TypeError(f"Amounts value {self.amounts} is not a list")
        else:
            for amount in self.amounts:
                if not isinstance(amount, Amount):
                    raise TypeError(f"Amount value {amount} is not a Amount")


class SessionUpdateMessage:
    def __init__(self, sws_name, msgs=None):
        self.sws_name = sws_name
        self._msgs = msgs or []
        self.validate()

    def __str__(self):
        string = f"<b>{self.sws_name}</b>\n\n"
        for index, msg in enumerate(self._msgs):
            string += f"<code>{msg}</code>"
            string += "\n\n" if index != len(self._msgs)-1 else ""
        return string

    def add_msg(self, msg: SessionMessage):
        self._msgs.append(msg)

    def validate(self):
        if not isinstance(self.sws_name, str):
            raise TypeError(f"SWS name {self.sws_name} is not a valid string")

    @classmethod
    def from_data(cls, sws_name, data):
        json_data = loads(data)
        instance = cls(sws_name)
        for _data in json_data:
            instance.add_msg(
                SessionMessage(session_name=_data.get("name"),
                               amounts=_data.get("amounts"))
            )
        return instance
