
class UnitsMissmatchException(TypeError):
    def __init__(self, u1, u2, operation="operation", notes=""):
        self.message = f"Units do not support {operation}: {u1} and {u2}. {notes}"
        super().__init__(self.message)

class UnitsConversionException(TypeError):
    def __init__(self, u1, u2, notes=""):
        self.message = f"Unable to convert units {u1} to {u2}. {notes}"
        super().__init__(self.message)

class UnitsConstructionException(RuntimeError):
    def __init__(self, ustring, usteps, msg="No other info."):
        self.message = f'Unable to construct "{ustring}" as unit. Found data steps:\n\t'
        if not len(usteps):
            self.message += "No other info supplied."
        else:
            self.message += "\n\t".join(f"{us}" for us in usteps)
        self.message += "\n" + msg
        super().__init__(self.message)