class PositionLimits:
    def __init__(self, max_single_weight: float = 0.20):
        self.max_single_weight = max_single_weight

    def check(self, symbol: str, value: float, total_value: float) -> bool:
        return value / total_value <= self.max_single_weight