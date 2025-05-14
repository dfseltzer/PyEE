
class UnitsMissmatchException(TypeError):
    def __init__(self, u1, u2, operation="operation", notes=""):
        self.message = f"Units do not support {operation}: {u1} and {u2}. {notes}"
        super().__init__(self.message)