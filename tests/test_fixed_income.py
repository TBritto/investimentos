import pytest

from src.analytics.fixed_income import (
    calculate_effective_annual_rate,
    calculate_net_value,
    compound_value,
    present_value,
    simulate_fixed_income,
)


def test_compound_value_for_prefixado() -> None:
    assert compound_value(1000.0, 0.10, 2) == pytest.approx(1210.0)


def test_ipca_plus_effective_rate_combines_inflation_and_coupon() -> None:
    rate = calculate_effective_annual_rate("IPCA+", 0.06, expected_ipca_annual_rate=0.04)

    assert rate == pytest.approx(0.1024)


def test_cdi_percentage_uses_contract_rate_as_percentage_of_cdi() -> None:
    rate = calculate_effective_annual_rate("percentual CDI", 1.10, expected_cdi_annual_rate=0.10)

    assert rate == pytest.approx(0.11)


def test_present_value_discounts_future_value() -> None:
    assert present_value(1210.0, 0.10, 2) == pytest.approx(1000.0)


def test_net_value_taxes_only_positive_gain() -> None:
    assert calculate_net_value(1000.0, 1200.0, 0.15) == pytest.approx(1170.0)


def test_market_marking_penalizes_when_current_rate_is_higher() -> None:
    result = simulate_fixed_income(
        invested_amount=1000.0,
        contracted_annual_rate=0.10,
        current_annual_rate=0.15,
        years_to_maturity=2,
        indexer="prefixado",
    )

    assert result.gross_value == pytest.approx(1210.0)
    assert result.estimated_price_today < result.gross_value
    assert result.rate_change_impact < result.gross_value - 1000.0
