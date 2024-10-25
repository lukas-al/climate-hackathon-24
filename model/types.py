from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class ClimateRiskType(Enum):
    """Types of climate risks that can affect households."""

    FLOOD = "flood"
    SUBSIDENCE = "subsidence"
    STORM = "storm"


@dataclass
class ClimateRisks:
    """Container for climate risk probabilities."""

    risks: Dict[ClimateRiskType, float] = field(default_factory=dict)

    def update_risks(self, change_rate: float) -> None:
        """Update all risk probabilities by the given rate."""
        for risk_type in self.risks:
            self.risks[risk_type] *= 1 + change_rate

    def apply_shock(self, magnitude: float) -> None:
        """Apply a shock multiplier to all risks."""
        for risk_type in self.risks:
            self.risks[risk_type] *= 1 + magnitude


@dataclass
class ClaimRecord:
    """Record of an insurance claim."""

    amount: float
    risk_type: ClimateRiskType
    timestamp: int  # Model step when claim was made


@dataclass
class InsurancePolicy:
    """Details of an insurance policy."""

    premium_rate: float
    risk_premium: float
    house_value: float

    def calculate_premium(self) -> float:
        """Calculate the total premium for this policy."""
        base_premium = self.house_value * self.premium_rate
        risk_adjustment = self.house_value * self.risk_premium
        return base_premium + risk_adjustment


@dataclass
class InsuranceMetrics:
    """Tracking metrics for insurance operations."""

    capital: float
    claims_paid: float = 0.0
    premiums_collected: float = 0.0
    profit_history: List[float] = field(default_factory=list)

    def record_profit(self) -> None:
        """Calculate and record profit for current period."""
        current_profit = self.premiums_collected - self.claims_paid
        self.profit_history.append(current_profit)
        self.claims_paid = 0.0
        self.premiums_collected = 0.0


@dataclass
class ModelConfig:
    """Configuration parameters for the model."""

    n_households: int
    n_insurers: int
    initial_insurer_capital: float
    climate_change_rate: float
    grid_width: int
    grid_height: int
    uk_shapefile_path: str
    base_risk_levels: Dict[ClimateRiskType, float]
    risk_volatility: float = 0.1
    max_risk_level: float = 0.5
