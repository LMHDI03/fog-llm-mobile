class Session:
    def __init__(self):
        self.history = []

    def add(self, role: str, text: str):
        self.history.append({"role": role, "text": text})

    def get_history(self):
        return self.history
