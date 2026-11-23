class ServiceError(Exception):
    def __init__(self, code: str, message: str, status: int = 503):
        super().__init__(code)  # Never include provider text or user data in exception messages.
        self.code = code
        self.message = message
        self.status = status
