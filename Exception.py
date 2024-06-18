class InvalidInputError(Exception):
    def __init__(self, message="Invalid input. Please enter a number."):
        self.message = message
        super().__init__(self.message)
