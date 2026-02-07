# app_services/data_service.py

class DataService:
    """
    Read-only data access for UI / API layers.
    """

    def __init__(self, loader):
        self.loader = loader

    def load(
        self,
        instrument,
        timeframe,
        start_date,
        end_date,
    ):
        return self.loader.load(
            instrument=instrument,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
        )
