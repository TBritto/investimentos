from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FixedIncomeSimulation:
    gross_value: float
    net_value: float
    estimated_price_today: float
    rate_change_impact: float
    educational_notes: list[str]


def simulate_fixed_income(
    invested_amount: float,
    contracted_annual_rate: float,
    current_annual_rate: float,
    years_to_maturity: float,
    indexer: str,
    income_tax_rate: float = 0.0,
    expected_ipca_annual_rate: float = 0.0,
    expected_cdi_annual_rate: float = 0.0,
) -> FixedIncomeSimulation:
    _validate_inputs(invested_amount, years_to_maturity, income_tax_rate)
    effective_rate = calculate_effective_annual_rate(
        indexer=indexer,
        contracted_annual_rate=contracted_annual_rate,
        expected_ipca_annual_rate=expected_ipca_annual_rate,
        expected_cdi_annual_rate=expected_cdi_annual_rate,
    )
    gross_value = compound_value(invested_amount, effective_rate, years_to_maturity)
    net_value = calculate_net_value(invested_amount, gross_value, income_tax_rate)
    estimated_price_today = present_value(gross_value, current_annual_rate, years_to_maturity)
    rate_change_impact = estimated_price_today - invested_amount

    notes = [
        "Simulacao aproximada para fins educacionais.",
        "Nao representa recomendacao de compra, venda ou manutencao.",
        "A marcacao a mercado usa desconto simplificado pela taxa atual informada.",
    ]

    return FixedIncomeSimulation(
        gross_value=gross_value,
        net_value=net_value,
        estimated_price_today=estimated_price_today,
        rate_change_impact=rate_change_impact,
        educational_notes=notes,
    )


def calculate_effective_annual_rate(
    indexer: str,
    contracted_annual_rate: float,
    expected_ipca_annual_rate: float = 0.0,
    expected_cdi_annual_rate: float = 0.0,
) -> float:
    normalized_indexer = indexer.strip().lower()
    if normalized_indexer == "prefixado":
        return contracted_annual_rate
    if normalized_indexer == "ipca+":
        return (1 + expected_ipca_annual_rate) * (1 + contracted_annual_rate) - 1
    if normalized_indexer in {"percentual cdi", "cdi"}:
        return expected_cdi_annual_rate * contracted_annual_rate

    raise ValueError("Indexador desconhecido. Use prefixado, IPCA+ ou percentual CDI.")


def compound_value(principal: float, annual_rate: float, years: float) -> float:
    return principal * ((1 + annual_rate) ** years)


def present_value(future_value: float, annual_discount_rate: float, years: float) -> float:
    return future_value / ((1 + annual_discount_rate) ** years)


def calculate_net_value(invested_amount: float, gross_value: float, income_tax_rate: float) -> float:
    taxable_gain = max(gross_value - invested_amount, 0.0)
    return gross_value - (taxable_gain * income_tax_rate)


def _validate_inputs(invested_amount: float, years_to_maturity: float, income_tax_rate: float) -> None:
    if invested_amount <= 0:
        raise ValueError("Valor investido precisa ser maior que zero.")
    if years_to_maturity <= 0:
        raise ValueError("Anos ate vencimento precisa ser maior que zero.")
    if income_tax_rate < 0 or income_tax_rate > 1:
        raise ValueError("Aliquota de IR deve estar entre 0% e 100%.")
