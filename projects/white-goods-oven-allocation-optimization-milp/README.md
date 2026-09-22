# White-Goods Oven Allocation Optimization with MILP

This repository presents a graduate-level allocation optimization case for a multinational white-goods manufacturer.

The case is intentionally generic. It does not represent, reproduce, or claim affiliation with any real company, brand, factory, customer, or commercial organization.

## Business Scenario

A multinational white-goods manufacturer operates a high-volume oven factory running three shifts per day. The plant manufactures four main oven families and several dozen commercial models for multiple international markets.

The monthly production plan has already been finalized by Production Planning. Therefore, the optimization problem is not to decide what should be produced. The available quantity of every oven model is fixed.

International sales organizations submit requested quantities for each model. Aggregate demand regularly exceeds available production. The manufacturer must therefore decide how many units of each model should be allocated to each country.

The allocation decision must consider more than total demand. Different markets have different strategic importance, contribution margins, minimum service expectations, premium-product requirements, and regional priorities.

The optimization problem is to determine the monthly product-country allocation matrix while respecting production, demand, commercial, service-level, and regional constraints.

## Problem Characteristics

The model contains:

- 36 oven models
- 4 product families
- 4 fictional brand labels used only as internal synthetic categories
- 24 country markets
- 4 commercial regions
- fixed monthly production quantities by model
- deterministic synthetic demand by model and country
- market-specific commercial value
- country-level minimum service constraints
- regional minimum and maximum allocation shares
- premium-product protection rules
- anti-starvation constraints
- product-family continuity constraints

## Sets

Let:

- `i in I` denote oven models
- `j in J` denote countries
- `r in R` denote commercial regions
- `f in F` denote oven families

## Parameters

- `P_i`: production plan quantity of model `i`
- `D_ij`: demand for model `i` in country `j`
- `D_j`: total demand of country `j`
- `V_ij`: commercial value of allocating model `i` to country `j`
- `lambda_j`: shortage penalty for country `j`
- `alpha_j`: minimum service level for selected strategic countries
- `beta_r^min`: minimum share of total production assigned to region `r`
- `beta_r^max`: maximum share of total production assigned to region `r`

## Decision Variable

`x_ij` = number of units of oven model `i` allocated to country `j`

with

`x_ij >= 0` and integer.

An additional shortage variable is used:

`u_j` = unmet demand in country `j`.

## Objective Function

The model maximizes weighted commercial value while penalizing unmet demand:

```text
maximize

sum(i,j) V_ij * x_ij
+ fulfillment_bonus
- sum(j) lambda_j * u_j
```

The weighted commercial value can be interpreted as a synthetic combination of margin, strategic-market importance, regional importance, and product-category attractiveness.

## Core Constraints

### 1. Production-plan conservation

For every model:

```text
sum(j) x_ij = P_i
```

All units in the finalized production plan must be allocated.

### 2. Demand upper bound

For every model-country pair:

```text
x_ij <= D_ij
```

No market can receive more units of a model than requested.

### 3. Unmet-demand balance

For every country:

```text
u_j = D_j - sum(i) x_ij
```

### 4. Strategic-market minimum service

For selected strategic markets:

```text
sum(i) x_ij >= alpha_j * D_j
```

### 5. Regional allocation bounds

For every region:

```text
beta_r^min * total_production
<= sum(i,j in r) x_ij
<= beta_r^max * total_production
```

### 6. Premium-product protection

Selected high-priority markets must receive a minimum percentage of their premium-product demand.

### 7. Anti-starvation rule

Every country receives at least a basic share of its total requested volume, preventing the optimizer from completely sacrificing lower-value markets.

### 8. Product-family continuity

If a country has material demand for a product family, the allocation model preserves a minimum presence of that family.

## Why This Is an Allocation Model

A common modeling error is to write constraints such as:

```python
x[model][country] == predetermined_allocation
```

That does not optimize allocation. It fixes the answer in advance and only checks feasibility.

In this repository, the allocation quantities are true decision variables. Production is fixed, demand is bounded, and the optimizer chooses the distribution.

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python oven_allocation.py
```

The script exports:

- `allocation_results.csv`
- `country_service_levels.csv`
- `model_statistics.csv`
- `regional_statistics.csv`
- `oven_allocation_report.xlsx`

## Suggested Graduate-Level Exercises

1. Reformulate the objective as a lexicographic optimization problem.
2. Introduce explicit fairness variables and minimize service-level dispersion.
3. Replace deterministic demand with demand scenarios.
4. Formulate a two-stage stochastic allocation model.
5. Introduce inventory carry-over across months.
6. Couple production planning and allocation in one integrated MILP.
7. Add transportation cost and regional distribution-center capacity.
8. Compare the optimal solution with proportional allocation heuristics.
9. Perform sensitivity analysis on strategic weights and shortage penalties.
10. Study the shadow-price interpretation of scarce production quantities.

## Disclaimer

All data, labels, quantities, brands, and commercial structures in this repository are synthetic and created solely for optimization modeling and educational analysis. No real company, trademark, factory, customer, or proprietary dataset is represented.