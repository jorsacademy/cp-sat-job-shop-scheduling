"""
White-Goods Oven Allocation Optimization
----------------------------------------

Graduate-level synthetic allocation case for a multinational
white-goods manufacturer.

The model allocates a fixed monthly oven production plan across
international sales markets whose aggregate demand exceeds supply.

Method:
    Mixed-Integer Linear Programming (MILP)

Solver:
    PuLP / CBC

Important:
    All company structures, labels, values, demand quantities, margins,
    priorities, and constraints in this script are synthetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import pulp


# ============================================================
# 1. DATA STRUCTURES
# ============================================================


@dataclass(frozen=True)
class Country:
    name: str
    region: str
    strategic_weight: float
    shortage_penalty: float
    minimum_service_level: float


@dataclass(frozen=True)
class OvenModel:
    code: str
    family: str
    brand_label: str
    production_plan: int
    base_margin: float
    premium: bool


# ============================================================
# 2. COUNTRY MASTER DATA
# ============================================================


COUNTRIES: List[Country] = [
    Country("Germany", "Western Europe", 1.35, 120.0, 0.62),
    Country("France", "Western Europe", 1.25, 110.0, 0.58),
    Country("United Kingdom", "Western Europe", 1.22, 108.0, 0.56),
    Country("Italy", "Western Europe", 1.18, 102.0, 0.52),
    Country("Spain", "Western Europe", 1.12, 96.0, 0.48),
    Country("Netherlands", "Western Europe", 1.10, 94.0, 0.48),
    Country("Poland", "Central & Eastern Europe", 1.18, 100.0, 0.52),
    Country("Czech Republic", "Central & Eastern Europe", 1.08, 88.0, 0.45),
    Country("Hungary", "Central & Eastern Europe", 1.04, 82.0, 0.42),
    Country("Romania", "Central & Eastern Europe", 1.03, 80.0, 0.40),
    Country("Bulgaria", "Central & Eastern Europe", 0.98, 74.0, 0.36),
    Country("Croatia", "Central & Eastern Europe", 0.97, 72.0, 0.35),
    Country("Türkiye", "Middle East & Türkiye", 1.30, 112.0, 0.58),
    Country("UAE", "Middle East & Türkiye", 1.20, 104.0, 0.50),
    Country("Saudi Arabia", "Middle East & Türkiye", 1.16, 100.0, 0.48),
    Country("Israel", "Middle East & Türkiye", 1.08, 90.0, 0.43),
    Country("Qatar", "Middle East & Türkiye", 1.04, 84.0, 0.38),
    Country("Kuwait", "Middle East & Türkiye", 1.03, 82.0, 0.38),
    Country("South Africa", "Africa & Emerging Markets", 1.05, 86.0, 0.42),
    Country("Morocco", "Africa & Emerging Markets", 0.97, 72.0, 0.34),
    Country("Egypt", "Africa & Emerging Markets", 1.00, 76.0, 0.36),
    Country("Algeria", "Africa & Emerging Markets", 0.94, 68.0, 0.32),
    Country("Kenya", "Africa & Emerging Markets", 0.90, 62.0, 0.28),
    Country("Tunisia", "Africa & Emerging Markets", 0.92, 65.0, 0.30),
]


# ============================================================
# 3. OVEN MODEL MASTER DATA
# ============================================================


OVEN_MODELS: List[OvenModel] = []

# Brand labels below are deliberately generic synthetic category labels.
FAMILIES = [
    ("STD", "Standard Built-In", False, 430.0),
    ("PRM", "Premium Built-In", True, 610.0),
    ("PYR", "Pyrolytic", True, 690.0),
    ("CMP", "Compact Combination", True, 760.0),
]

BRAND_LABELS = ["Brand-A", "Brand-B", "Brand-C", "Brand-D"]

for family_index, (prefix, family, premium, margin) in enumerate(FAMILIES):
    for model_number in range(1, 10):
        model_code = f"{prefix}-{model_number:02d}"
        brand_label = BRAND_LABELS[(family_index + model_number - 1) % len(BRAND_LABELS)]

        # Deterministic synthetic production profile.
        production = (
            390
            + family_index * 28
            + model_number * 13
            + ((model_number * 17 + family_index * 11) % 95)
        )

        adjusted_margin = margin + model_number * 9 + family_index * 18

        OVEN_MODELS.append(
            OvenModel(
                code=model_code,
                family=family,
                brand_label=brand_label,
                production_plan=production,
                base_margin=adjusted_margin,
                premium=premium,
            )
        )


# ============================================================
# 4. DETERMINISTIC SYNTHETIC DEMAND
# ============================================================


def build_demand() -> Dict[Tuple[str, str], int]:
    """Build a deterministic demand matrix with structural scarcity."""

    demand: Dict[Tuple[str, str], int] = {}

    for i, model in enumerate(OVEN_MODELS):
        for j, country in enumerate(COUNTRIES):
            market_size_factor = 0.75 + ((j * 7) % 11) / 10.0
            model_popularity = 0.80 + ((i * 5 + j * 3) % 9) / 10.0
            strategic_boost = country.strategic_weight

            premium_adjustment = 1.0
            if model.premium:
                if country.name in {
                    "Germany",
                    "France",
                    "United Kingdom",
                    "Türkiye",
                    "UAE",
                }:
                    premium_adjustment = 1.25
                else:
                    premium_adjustment = 0.88

            raw_demand = (
                model.production_plan
                / 8.5
                * market_size_factor
                * model_popularity
                * strategic_boost
                * premium_adjustment
            )

            demand[(model.code, country.name)] = max(5, int(round(raw_demand)))

    return demand


DEMAND = build_demand()


# ============================================================
# 5. COMMERCIAL VALUE
# ============================================================


def contribution_value(model: OvenModel, country: Country) -> float:
    regional_factor = {
        "Western Europe": 1.12,
        "Central & Eastern Europe": 0.98,
        "Middle East & Türkiye": 1.06,
        "Africa & Emerging Markets": 0.88,
    }[country.region]

    brand_factor = {
        "Brand-A": 1.08,
        "Brand-B": 1.12,
        "Brand-C": 0.96,
        "Brand-D": 0.92,
    }[model.brand_label]

    return (
        model.base_margin
        * country.strategic_weight
        * regional_factor
        * brand_factor
    )


VALUE = {
    (model.code, country.name): contribution_value(model, country)
    for model in OVEN_MODELS
    for country in COUNTRIES
}


# ============================================================
# 6. AGGREGATIONS
# ============================================================


COUNTRY_TOTAL_DEMAND = {
    country.name: sum(DEMAND[(model.code, country.name)] for model in OVEN_MODELS)
    for country in COUNTRIES
}

TOTAL_PRODUCTION = sum(model.production_plan for model in OVEN_MODELS)

REGION_COUNTRIES: Dict[str, List[str]] = {}
for country in COUNTRIES:
    REGION_COUNTRIES.setdefault(country.region, []).append(country.name)

REGIONAL_MIN_SHARE = {
    "Western Europe": 0.31,
    "Central & Eastern Europe": 0.20,
    "Middle East & Türkiye": 0.20,
    "Africa & Emerging Markets": 0.10,
}

REGIONAL_MAX_SHARE = {
    "Western Europe": 0.48,
    "Central & Eastern Europe": 0.32,
    "Middle East & Türkiye": 0.32,
    "Africa & Emerging Markets": 0.22,
}

STRATEGIC_COUNTRIES = {
    "Germany",
    "France",
    "United Kingdom",
    "Poland",
    "Türkiye",
    "UAE",
}

PREMIUM_PRIORITY_COUNTRIES = {
    "Germany",
    "France",
    "United Kingdom",
    "Türkiye",
    "UAE",
}


# ============================================================
# 7. OPTIMIZATION MODEL
# ============================================================


problem = pulp.LpProblem(
    "White_Goods_Oven_Allocation_Optimization",
    pulp.LpMaximize,
)


# ============================================================
# 8. DECISION VARIABLES
# ============================================================


allocation = pulp.LpVariable.dicts(
    "Allocation",
    (
        [m.code for m in OVEN_MODELS],
        [c.name for c in COUNTRIES],
    ),
    lowBound=0,
    cat=pulp.LpInteger,
)

unmet_demand = pulp.LpVariable.dicts(
    "UnmetDemand",
    [c.name for c in COUNTRIES],
    lowBound=0,
    cat=pulp.LpContinuous,
)


# ============================================================
# 9. OBJECTIVE FUNCTION
# ============================================================


commercial_value = pulp.lpSum(
    VALUE[(model.code, country.name)] * allocation[model.code][country.name]
    for model in OVEN_MODELS
    for country in COUNTRIES
)

shortage_cost = pulp.lpSum(
    country.shortage_penalty * unmet_demand[country.name]
    for country in COUNTRIES
)

fulfillment_bonus = pulp.lpSum(
    8.0 * country.strategic_weight * allocation[model.code][country.name]
    for model in OVEN_MODELS
    for country in COUNTRIES
)

problem += (
    commercial_value + fulfillment_bonus - shortage_cost,
    "Total_Weighted_Commercial_Value",
)


# ============================================================
# 10. CONSTRAINTS
# ============================================================


# 10.1 Production-plan conservation
for model in OVEN_MODELS:
    problem += (
        pulp.lpSum(
            allocation[model.code][country.name]
            for country in COUNTRIES
        )
        == model.production_plan,
        f"ProductionPlan_{model.code}",
    )


# 10.2 Demand ceilings
for model in OVEN_MODELS:
    for country in COUNTRIES:
        problem += (
            allocation[model.code][country.name]
            <= DEMAND[(model.code, country.name)],
            f"Demand_{model.code}_{country.name}",
        )


# 10.3 Unmet-demand balance
for country in COUNTRIES:
    allocated_to_country = pulp.lpSum(
        allocation[model.code][country.name]
        for model in OVEN_MODELS
    )

    problem += (
        unmet_demand[country.name]
        == COUNTRY_TOTAL_DEMAND[country.name] - allocated_to_country,
        f"UnmetDemandBalance_{country.name}",
    )


# 10.4 Strategic-market minimum service levels
for country in COUNTRIES:
    if country.name in STRATEGIC_COUNTRIES:
        allocated_to_country = pulp.lpSum(
            allocation[model.code][country.name]
            for model in OVEN_MODELS
        )

        problem += (
            allocated_to_country
            >= country.minimum_service_level * COUNTRY_TOTAL_DEMAND[country.name],
            f"StrategicService_{country.name}",
        )


# 10.5 Regional minimum shares
for region, minimum_share in REGIONAL_MIN_SHARE.items():
    regional_allocation = pulp.lpSum(
        allocation[model.code][country_name]
        for model in OVEN_MODELS
        for country_name in REGION_COUNTRIES[region]
    )

    problem += (
        regional_allocation >= minimum_share * TOTAL_PRODUCTION,
        f"RegionalMinimum_{region}",
    )


# 10.6 Regional maximum shares
for region, maximum_share in REGIONAL_MAX_SHARE.items():
    regional_allocation = pulp.lpSum(
        allocation[model.code][country_name]
        for model in OVEN_MODELS
        for country_name in REGION_COUNTRIES[region]
    )

    problem += (
        regional_allocation <= maximum_share * TOTAL_PRODUCTION,
        f"RegionalMaximum_{region}",
    )


# 10.7 Premium-product protection
premium_models = [model for model in OVEN_MODELS if model.premium]

for country in COUNTRIES:
    if country.name in PREMIUM_PRIORITY_COUNTRIES:
        premium_demand = sum(
            DEMAND[(model.code, country.name)]
            for model in premium_models
        )

        premium_allocation = pulp.lpSum(
            allocation[model.code][country.name]
            for model in premium_models
        )

        problem += (
            premium_allocation >= 0.35 * premium_demand,
            f"PremiumProtection_{country.name}",
        )


# 10.8 Anti-starvation rule
for country in COUNTRIES:
    total_country_allocation = pulp.lpSum(
        allocation[model.code][country.name]
        for model in OVEN_MODELS
    )

    problem += (
        total_country_allocation >= 0.18 * COUNTRY_TOTAL_DEMAND[country.name],
        f"AntiStarvation_{country.name}",
    )


# 10.9 Product-family continuity
families_in_model = sorted(set(model.family for model in OVEN_MODELS))

for country in COUNTRIES:
    for family in families_in_model:
        models_in_family = [
            model for model in OVEN_MODELS if model.family == family
        ]

        family_demand = sum(
            DEMAND[(model.code, country.name)]
            for model in models_in_family
        )

        family_allocation = pulp.lpSum(
            allocation[model.code][country.name]
            for model in models_in_family
        )

        if family_demand >= 100:
            safe_family = family.replace(" ", "_").replace("&", "and")
            safe_country = country.name.replace(" ", "_").replace("&", "and")

            problem += (
                family_allocation >= 0.08 * family_demand,
                f"FamilyContinuity_{safe_country}_{safe_family}",
            )


# ============================================================
# 11. SOLVE
# ============================================================


solver = pulp.PULP_CBC_CMD(
    msg=True,
    timeLimit=300,
    gapRel=0.001,
)

problem.solve(solver)

status = pulp.LpStatus[problem.status]

print("=" * 80)
print("WHITE-GOODS OVEN ALLOCATION OPTIMIZATION")
print("=" * 80)
print(f"Solver status: {status}")
print()

if status not in {"Optimal", "Feasible"}:
    raise RuntimeError(
        f"No usable allocation solution found. Solver status: {status}"
    )


# ============================================================
# 12. ALLOCATION TABLE
# ============================================================


allocation_records = []

for model in OVEN_MODELS:
    for country in COUNTRIES:
        qty = allocation[model.code][country.name].value() or 0

        if qty > 0:
            demand_qty = DEMAND[(model.code, country.name)]

            allocation_records.append(
                {
                    "Model": model.code,
                    "Family": model.family,
                    "Brand_Label": model.brand_label,
                    "Country": country.name,
                    "Region": country.region,
                    "Demand": demand_qty,
                    "Allocation": int(round(qty)),
                    "Fill_Rate": qty / demand_qty,
                    "Unit_Value": VALUE[(model.code, country.name)],
                    "Commercial_Value": qty * VALUE[(model.code, country.name)],
                }
            )

allocation_df = pd.DataFrame(allocation_records)


# ============================================================
# 13. COUNTRY KPI REPORT
# ============================================================


country_records = []

for country in COUNTRIES:
    total_demand = COUNTRY_TOTAL_DEMAND[country.name]

    total_allocated = sum(
        allocation[model.code][country.name].value() or 0
        for model in OVEN_MODELS
    )

    shortage = total_demand - total_allocated
    service_level = total_allocated / total_demand if total_demand > 0 else 0

    commercial_value_country = sum(
        (allocation[model.code][country.name].value() or 0)
        * VALUE[(model.code, country.name)]
        for model in OVEN_MODELS
    )

    country_records.append(
        {
            "Country": country.name,
            "Region": country.region,
            "Demand": int(total_demand),
            "Allocated": int(round(total_allocated)),
            "Unmet_Demand": int(round(shortage)),
            "Service_Level": service_level,
            "Strategic_Weight": country.strategic_weight,
            "Commercial_Value": commercial_value_country,
        }
    )

country_df = pd.DataFrame(country_records).sort_values(
    by="Service_Level",
    ascending=False,
)


# ============================================================
# 14. MODEL KPI REPORT
# ============================================================


model_records = []

for model in OVEN_MODELS:
    total_requested = sum(
        DEMAND[(model.code, country.name)]
        for country in COUNTRIES
    )

    total_allocated = sum(
        allocation[model.code][country.name].value() or 0
        for country in COUNTRIES
    )

    model_records.append(
        {
            "Model": model.code,
            "Family": model.family,
            "Brand_Label": model.brand_label,
            "Production_Plan": model.production_plan,
            "Total_Demand": total_requested,
            "Allocated": int(round(total_allocated)),
            "Demand_to_Supply_Ratio": total_requested / model.production_plan,
        }
    )

model_df = pd.DataFrame(model_records).sort_values(
    by="Demand_to_Supply_Ratio",
    ascending=False,
)


# ============================================================
# 15. REGION KPI REPORT
# ============================================================


region_records = []

for region, countries in REGION_COUNTRIES.items():
    region_demand = sum(
        COUNTRY_TOTAL_DEMAND[country]
        for country in countries
    )

    region_allocation = sum(
        allocation[model.code][country].value() or 0
        for model in OVEN_MODELS
        for country in countries
    )

    region_records.append(
        {
            "Region": region,
            "Demand": int(region_demand),
            "Allocation": int(round(region_allocation)),
            "Service_Level": region_allocation / region_demand,
            "Share_of_Production": region_allocation / TOTAL_PRODUCTION,
        }
    )

region_df = pd.DataFrame(region_records)


# ============================================================
# 16. GLOBAL KPI
# ============================================================


total_demand = sum(COUNTRY_TOTAL_DEMAND.values())
total_allocated = int(round(allocation_df["Allocation"].sum()))
total_unmet = total_demand - total_allocated
global_service_level = total_allocated / total_demand
objective_value = pulp.value(problem.objective)


# ============================================================
# 17. PRINT RESULTS
# ============================================================


print("GLOBAL KPI")
print("-" * 80)
print(f"Total production : {TOTAL_PRODUCTION:,.0f}")
print(f"Total demand     : {total_demand:,.0f}")
print(f"Total allocated  : {total_allocated:,.0f}")
print(f"Unmet demand     : {total_unmet:,.0f}")
print(f"Global service   : {global_service_level:.2%}")
print(f"Objective value  : {objective_value:,.2f}")
print()

print("COUNTRY SERVICE LEVELS")
print("-" * 80)

display_country = country_df.copy()
display_country["Service_Level"] = display_country["Service_Level"].map(
    lambda x: f"{x:.2%}"
)

print(
    display_country[
        [
            "Country",
            "Region",
            "Demand",
            "Allocated",
            "Unmet_Demand",
            "Service_Level",
        ]
    ].to_string(index=False)
)
print()

print("REGIONAL PERFORMANCE")
print("-" * 80)

display_region = region_df.copy()
display_region["Service_Level"] = display_region["Service_Level"].map(
    lambda x: f"{x:.2%}"
)
display_region["Share_of_Production"] = display_region[
    "Share_of_Production"
].map(lambda x: f"{x:.2%}")

print(display_region.to_string(index=False))
print()

print("MOST CAPACITY-CONSTRAINED MODELS")
print("-" * 80)

print(
    model_df[
        [
            "Model",
            "Family",
            "Brand_Label",
            "Production_Plan",
            "Total_Demand",
            "Demand_to_Supply_Ratio",
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 18. EXPORT RESULTS
# ============================================================


allocation_df.to_csv("allocation_results.csv", index=False)
country_df.to_csv("country_service_levels.csv", index=False)
model_df.to_csv("model_statistics.csv", index=False)
region_df.to_csv("regional_statistics.csv", index=False)

with pd.ExcelWriter("oven_allocation_report.xlsx", engine="openpyxl") as writer:
    allocation_df.to_excel(writer, sheet_name="Allocation", index=False)
    country_df.to_excel(writer, sheet_name="Country KPI", index=False)
    model_df.to_excel(writer, sheet_name="Model KPI", index=False)
    region_df.to_excel(writer, sheet_name="Region KPI", index=False)

print()
print("Files generated:")
print("  allocation_results.csv")
print("  country_service_levels.csv")
print("  model_statistics.csv")
print("  regional_statistics.csv")
print("  oven_allocation_report.xlsx")
