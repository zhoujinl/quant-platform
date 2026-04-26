class StopLoss:
    def __init__(self, stop_pct: float = -0.10):
        self.stop_pct = stop_pct

    def should_stop(self, entry_price: float, current_price: float) -> bool:
        return (current_price / entry_price - 1) <= self.stop_pct


class TimeStop:
    def __init__(self, max_days: int = 20):
        self.max_days = max_days

    def should_stop(self, hold_days: int) -> bool:
        return hold_days >= self.max_days