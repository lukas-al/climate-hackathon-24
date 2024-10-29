from typing import List, Tuple
import mesa
import numpy as np
from .agents import Household, Insurer, GridCell
from .types import ModelConfig, ClimateRisks, InsurancePolicy
from .utils import create_model_reporters, create_agent_reporters, load_uk_boundaries


class ClimateInsuranceModel(mesa.Model):
    """Model of climate risk interactions between households and insurers."""

    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.grid = mesa.space.MultiGrid(config.grid_width, config.grid_height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.uk_boundaries = load_uk_boundaries(config.uk_shapefile_path)
        self.insurers = []
        self._create_grid_cells()
        self._create_insurers()
        self._create_households()
        self.datacollector = mesa.DataCollector(
            model_reporters=create_model_reporters(),
            agent_reporters=create_agent_reporters(),
        )

    def _create_grid_cells(self) -> None:
        """Create grid cells with initial climate risks."""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                climate_risks = ClimateRisks(
                    {
                        risk_type: base_prob
                        for risk_type, base_prob in self.config.base_risk_levels.items()
                    }
                )
                pos = (x, y)
                cell = GridCell(f"cell_{x}_{y}", self, climate_risks, pos)
                self.grid.place_agent(cell, pos)
                self.schedule.add(cell)

    def _create_insurers(self) -> None:
        """Create insurer agents."""
        for i in range(self.config.n_insurers):
            insurer = Insurer(
                unique_id=i,
                model=self,
                initial_capital=self.config.initial_insurer_capital,
            )
            self.insurers.append(insurer)
            self.schedule.add(insurer)

    def _create_households(self) -> None:
        """Create household agents."""
        for i in range(self.config.n_households):
            pos = self._get_random_valid_position() # Randomly allocate
            
            house_value = self.random.normalvariate(2000000, 500000)
            household = Household(i + self.config.n_insurers, self, pos, house_value)

            insurer = self.random.choice(self.insurers)
            household.insurer = insurer
            insurer.insured_households.add(household)

            household.policy = InsurancePolicy(
                premium_rate=insurer.base_premium_rate,
                risk_premium=insurer.risk_premium,
                house_value=house_value,
            )

            self.grid.place_agent(household, pos)
            self.schedule.add(household)

    def _get_random_valid_position(self) -> Tuple[int, int]:
        """Get a random position within valid UK boundaries."""
        return (
            self.random.randrange(self.grid.width),
            self.random.randrange(self.grid.height),
        )

    def _calculate_mean_climate_risk(self) -> float:
        """Calculate the mean climate risk across all grid cells."""
        grid_cells = [
            agent for agent in self.schedule.agents if isinstance(agent, GridCell)
        ]
        risk_values = []
        for cell in grid_cells:
            risk_values.extend(cell.climate_risks.risks.values())
        return np.mean(risk_values) if risk_values else 0.0

    def apply_climate_shock(
        self, affected_positions: List[Tuple], shock_magnitude: float, duration: int
    ) -> None:
        """Apply a climate shock to specific grid cells."""
        for pos in affected_positions:
            cell_contents = self.grid.get_cell_list_contents([pos])
            grid_cell = next(
                (agent for agent in cell_contents if isinstance(agent, GridCell)), None
            )
            if grid_cell:
                print(f"Applying shock to grid cell {grid_cell.pos}")
                grid_cell.climate_risks.apply_shock(shock_magnitude)

    def step(self) -> None:
        """Advance the model by one step."""
        self.datacollector.collect(self)
        self.schedule.step()
