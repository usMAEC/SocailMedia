
from json import JSONEncoder
class MSchedule:
    def __init__(self, name, age):
        self.name = name  # Instance attribute
        self.age = age    # Instance attribute

class MScheduleEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
