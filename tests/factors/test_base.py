import pytest
import pandas as pd
import numpy as np
from src.factors.base import PE, PB, MarketCap, ROE, Momentum
from src.factors.registry import get_factor, FACTOR_REGISTRY


class TestPEFactor:
    def test_pe_basic(self):
        df = pd.DataFrame({
            'close': [100, 200, 150],
            'eps': [2, 4, 3]
        }, index=['600519.SH', '000001.SZ', '000002.SZ'])
        pe = PE()
        result = pe.compute(df)
        np.testing.assert_array_almost_equal(result.values, [50, 50, 50])

    def test_pe_with_zero_eps(self):
        df = pd.DataFrame({
            'close': [100, 200],
            'eps': [2, 0]
        }, index=['600519.SH', '000001.SZ'])
        pe = PE()
        result = pe.compute(df)
        assert result['600519.SH'] == 50
        assert np.isinf(result['000001.SZ'])


class TestPBFactor:
    def test_pb_basic(self):
        df = pd.DataFrame({
            'close': [100, 200],
            'bps': [10, 20]
        }, index=['600519.SH', '000001.SZ'])
        pb = PB()
        result = pb.compute(df)
        np.testing.assert_array_almost_equal(result.values, [10, 10])


class TestMarketCapFactor:
    def test_marketcap_basic(self):
        df = pd.DataFrame({
            'close': [100, 200],
            'shares': [1e9, 2e9]
        }, index=['600519.SH', '000001.SZ'])
        mc = MarketCap()
        result = mc.compute(df)
        np.testing.assert_array_almost_equal(result.values, [100e9, 400e9])


class TestROEFactor:
    def test_roe_basic(self):
        df = pd.DataFrame({
            'net_profit': [10, 20],
            'equity': [100, 200]
        }, index=['600519.SH', '000001.SZ'])
        roe = ROE()
        result = roe.compute(df)
        np.testing.assert_array_almost_equal(result.values, [0.1, 0.1])


class TestMomentumFactor:
    def test_momentum_1d(self):
        df = pd.DataFrame({
            'close': [100, 110, 121]
        })
        mom = Momentum(period=1)
        result = mom.compute(df)
        assert abs(result.iloc[-1] - 0.10) < 1e-6

    def test_momentum_5d(self):
        df = pd.DataFrame({
            'close': [100, 110, 120, 130, 140, 150]
        })
        mom = Momentum(period=5)
        result = mom.compute(df)
        assert abs(result.iloc[-1] - 0.50) < 1e-6


class TestFactorRegistry:
    def test_get_factor_pe(self):
        pe_cls = get_factor('PE')
        pe = pe_cls()
        assert isinstance(pe, PE)

    def test_get_factor_momentum(self):
        mom_cls = get_factor('Momentum')
        mom = mom_cls(period=1)
        assert isinstance(mom, Momentum)

    def test_get_factor_invalid(self):
        with pytest.raises(ValueError, match='Unknown factor'):
            get_factor('INVALID')

    def test_registry_keys(self):
        assert 'PE' in FACTOR_REGISTRY
        assert 'PB' in FACTOR_REGISTRY
        assert 'MARKETCAP' in FACTOR_REGISTRY
        assert 'ROE' in FACTOR_REGISTRY
        assert 'MOMENTUM' in FACTOR_REGISTRY