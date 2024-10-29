from typing import Optional, List, Set, Tuple
import mesa
from .types import (
    InsurancePolicy,
    ClimateRisks,
    ClimateRiskType,
    ClaimRecord,
    InsuranceMetrics,
)


class GridCell(mesa.Agent):
    """A spatial grid cell containing climate risk information."""

    def __init__(
        self,
        unique_id: str,
        model: "ClimateInsuranceModel",
        climate_risks: ClimateRisks,
        pos: Tuple[int, int],  # Add position parameter
    ) -> None:
        super().__init__(unique_id, model)
        self.climate_risks: ClimateRisks = climate_risks
        self.pos = pos  # Store position as tuple

    def step(self) -> None:
        """Update climate risks according to model parameters."""
        self.climate_risks.update_risks(self.model.config.climate_change_rate)


class Household(mesa.Agent):
    """A household agent with a location and house value."""

    def __init__(
        self,
        unique_id: int,
        model: "ClimateInsuranceModel",
        pos: Tuple[int, int],  # Change to tuple
        house_value: float,
    ) -> None:
        super().__init__(unique_id, model)
        self.pos = pos  # Store position as tuple
        self.house_value: float = house_value
        self.insurer: Optional["Insurer"] = None
        self.claims_history: List[ClaimRecord] = []
        self.policy: Optional[InsurancePolicy] = None

    def step(self) -> None:
        """Check for climate events and file claims."""
        if not self.insurer or not self.policy:
            return

        grid_cell = self.model.grid.get_cell_list_contents([self.pos])[0]
        if not isinstance(grid_cell, GridCell):
            return

        for risk_type, probability in grid_cell.climate_risks.risks.items():
            if self.random.random() < probability:
                claim_amount = self._calculate_claim_amount(risk_type)
                self._file_claim(claim_amount, risk_type)

    def _calculate_claim_amount(self, risk_type: ClimateRiskType) -> float:
        """Calculate claim amount based on risk type and house value."""
        return self.house_value * 0.1

    def _file_claim(self, amount: float, risk_type: ClimateRiskType) -> None:
        """File a claim with the insurer."""
        if self.insurer:
            self.insurer.receive_claim(self, amount)
            self.claims_history.append(
                ClaimRecord(
                    amount=amount,
                    risk_type=risk_type,
                    timestamp=self.model.schedule.steps,
                )
            )


class Insurer(mesa.Agent):
    """An insurance company that collects premiums and pays claims."""

    def __init__(
        self, unique_id: int, model: "ClimateInsuranceModel", initial_capital: float
    ) -> None:
        super().__init__(unique_id, model)
        self.metrics = InsuranceMetrics(capital=initial_capital)
        self.base_premium_rate: float = 0.001
        self.risk_premium: float = 0.005
        self.insured_households: Set[Household] = set()

    def step(self) -> None:
        """Perform insurance operations for the current step."""
        self._collect_premiums()
        self._update_risk_premium()
        self.metrics.record_profit()

    def _collect_premiums(self) -> None:
        """Collect premiums from all insured households."""
        for household in self.insured_households:
            if household.policy:
                premium = household.policy.calculate_premium()
                self.metrics.capital += premium
                self.metrics.premiums_collected += premium

    def _update_risk_premium(self) -> None:
        """Update risk premium based on recent profit history."""
        recent_profits = (
            self.metrics.profit_history[-5:]
            if len(self.metrics.profit_history) > 5
            else self.metrics.profit_history
        )

        if sum(recent_profits) < 0:
            self.risk_premium *= 1.1
        else:
            self.risk_premium *= 0.95

    def receive_claim(self, household: Household, amount: float) -> None:
        """Process a claim from a household."""
        self.metrics.capital -= amount
        self.metrics.claims_paid += amount
