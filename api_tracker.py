import csv
import os
from datetime import datetime
from pathlib import Path

class ZerodhaAPITracker:
    def __init__(self):
        self.log_file = Path("zerodha_api_calls.csv")
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'endpoint', 'params', 'response_count', 'cost_estimate'])
    
    def log_call(self, endpoint: str, params: dict = None, response_count: int = 0):
        cost = self._estimate_cost(endpoint, response_count)
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                endpoint,
                str(params) if params else '',
                response_count,
                cost
            ])
        
        print(f"API Call: {endpoint} | Count: {response_count} | Est. Cost: ₹{cost}")
    
    def _estimate_cost(self, endpoint: str, count: int) -> float:
        # Zerodha API costs (approximate)
        if endpoint == 'instruments':
            return 0.0  # Free
        elif endpoint == 'historical_data':
            return 0.25  # ₹0.25 per call
        return 0.0

# Global tracker instance
api_tracker = ZerodhaAPITracker()