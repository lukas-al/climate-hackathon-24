from typing import Dict, Callable
import geopandas as gpd
import numpy as np
from .agents import Insurer


def create_model_reporters() -> Dict[str, Callable]:
    """Create the standard set of model-level metric reporters."""
    return {
        "Mean_Premium": lambda m: np.mean(
            [ins.risk_premium for ins in m.insurers]
        ),
        "Total_Insurer_Capital": lambda m: sum(
            [ins.metrics.capital for ins in m.insurers]
        ),
        "Mean_Climate_Risk": lambda m: m._calculate_mean_climate_risk(),
    }


def create_agent_reporters() -> Dict[str, Callable]:
    """Create the standard set of agent-level metric reporters."""
    return {
        "Capital": lambda a: getattr(a, "metrics", None).capital
        if isinstance(a, Insurer)
        else None,
        "Claims_Paid": lambda a: getattr(a, "metrics", None).claims_paid
        if isinstance(a, Insurer)
        else None,
        "Premiums_Collected": lambda a: getattr(a, "metrics", None).premiums_collected
        if isinstance(a, Insurer)
        else None,
    }


def load_uk_boundaries(shapefile_path: str) -> gpd.GeoDataFrame:
    """Load and process UK boundary data."""
    return gpd.read_file(shapefile_path)


def convert_to_grid_coordinates(
    lat: float, lon: float, grid_width: int, grid_height: int
) -> tuple[int, int]:
    """Convert latitude/longitude to grid coordinates."""
    # Implementation needed - this is a placeholder
    x = int((lon + 180) * (grid_width / 360))
    y = int((lat + 90) * (grid_height / 180))
    return x, y
