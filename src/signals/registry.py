from src.signals.generator import TopNSignal, ThresholdSignal, CompositeSignal


SIGNAL_REGISTRY = {
    'top_n': TopNSignal,
    'threshold': ThresholdSignal,
    'composite': CompositeSignal,
}


def get_signal(name: str, **kwargs):
    """获取信号实例
    
    Args:
        name: 信号名称
        **kwargs: 信号参数
        
    Returns:
        Signal实例
    """
    if name not in SIGNAL_REGISTRY:
        raise ValueError(f"Unknown signal: {name}")
    return SIGNAL_REGISTRY[name](**kwargs)