---
name: physics
description: Realizability checks for OMEGA strategies: settlement constraints, boundary conditions, and volume-clock consistency.
---

# Skill: Physics Engine (Realizability)

## Description
Ensures all strategies and trades obey market physics and exchange constraints.

## Capabilities

### 1. Settlement constraints
- Check T+1 explicitly: `sellable_volume <= yesterday_holdings`.
- Reject physically impossible plans (`trade.sell_amount > sellable_volume`).
- Treat T+1 as hard constraint (per Constitution Article IV), not a tunable heuristic.

### 2. Boundary conditions
- Validate limit-up/limit-down proximity before execution.
- If boundary state is active, disable assumptions of continuous liquidity.

### 3. Volume clock consistency
- Ensure SRL and impact logic run in volume-clock-consistent representation.
- Reject logic that infers impact only from wall-clock granularity.

## Verification protocol
- [ ] No selling beyond settleable inventory.
- [ ] No infinite-liquidity assumption at boundary prices.
- [ ] Volume-clock assumptions are consistent end-to-end.
