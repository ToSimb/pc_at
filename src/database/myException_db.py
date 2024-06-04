class MyException427_db(Exception):
    def __init__(self, message="427:"):
        self.message = message
        super().__init__(self.message)

class MyException527_db(Exception):
    def __init__(self, message="527:"):
        self.message = message
        super().__init__(self.message)