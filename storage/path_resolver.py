import os
from dtos.data_request_dto import DataRequestDTO

class PathResolver:
    """
    Resolves filesystem paths for parquet datasets.
    """

    def __init__(self, base_data_dir: str):
        self.base_data_dir = base_data_dir

    def get_parquet_path(self, request: DataRequestDTO) -> str:
        """
        Returns the absolute parquet file path for a given data request.
        Does NOT create directories or files.
        """

        exchange = request.instrument.exchange
        symbol = request.instrument.tradingsymbol
        timeframe = request.timeframe.code
        year = request.year

        return os.path.join(
            self.base_data_dir,
            "parquet",
            exchange,
            symbol,
            timeframe,
            f"{year}.parquet",
        )
