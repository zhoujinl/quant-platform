import pytest
import pandas as pd
from src.signals.generator import TopNSignal, ThresholdSignal, CompositeSignal


@pytest.fixture
def sample_factors():
    return pd.Series({
        '000001': 10.0,
        '000002': 20.0,
        '000003': 30.0,
        '000004': 40.0,
        '000005': 50.0,
    })


class TestTopNSignal:
    def test_generate_descending(self, sample_factors):
        signal = TopNSignal(n=3, ascending=False)
        result = signal.generate(sample_factors)
        assert len(result) == 3
        assert list(result.index) == ['000005', '000004', '000003']
    
    def test_generate_ascending(self, sample_factors):
        signal = TopNSignal(n=3, ascending=True)
        result = signal.generate(sample_factors)
        assert len(result) == 3
        assert list(result.index) == ['000001', '000002', '000003']


class TestThresholdSignal:
    def test_generate_gt(self, sample_factors):
        signal = ThresholdSignal(threshold=25, operator='gt')
        result = signal.generate(sample_factors)
        assert len(result) == 3
        assert '000001' not in result.index
        assert '000005' in result.index
    
    def test_generate_ge(self, sample_factors):
        signal = ThresholdSignal(threshold=30, operator='ge')
        result = signal.generate(sample_factors)
        assert len(result) == 3
    
    def test_generate_lt(self, sample_factors):
        signal = ThresholdSignal(threshold=30, operator='lt')
        result = signal.generate(sample_factors)
        assert len(result) == 2
        assert '000001' in result.index
    
    def test_generate_le(self, sample_factors):
        signal = ThresholdSignal(threshold=30, operator='le')
        result = signal.generate(sample_factors)
        assert len(result) == 3


class TestCompositeSignal:
    def test_generate_and(self):
        factors1 = pd.Series({'A': 1.0, 'B': 2.0, 'C': 3.0})
        factors2 = pd.Series({'B': 1.0, 'C': 2.0, 'D': 3.0})
        factors3 = pd.Series({'C': 1.0, 'D': 2.0, 'E': 3.0})
        
        signal = CompositeSignal([])
        result = signal.generate([factors1, factors2, factors3])
        
        assert len(result) == 1
        assert 'C' in result.index
        assert result['C'] == 1.0