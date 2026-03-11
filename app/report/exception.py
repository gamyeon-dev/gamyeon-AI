class ReportGenerationError(Exception):
    def __init__(self, code: str):
        self.code = code
