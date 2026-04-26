from src.factors.base import PE, PB, MarketCap, ROE, Momentum


FACTOR_REGISTRY = {
    'PE': PE,
    'PB': PB,
    'MARKETCAP': MarketCap,
    'ROE': ROE,
    'MOMENTUM': Momentum,
}


def get_factor(name: str) -> type:
    """获取因子类
    
    Args:
        name: 因子名称
    
    Returns:
        因子类
    
    Raises:
        ValueError: 未知因子
    """
    name_upper = name.upper()
    if name_upper in FACTOR_REGISTRY:
        return FACTOR_REGISTRY[name_upper]
    raise ValueError(f"Unknown factor: {name}")