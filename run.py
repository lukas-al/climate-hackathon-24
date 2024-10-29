from model.model import ClimateInsuranceModel
from model.types import ModelConfig, ClimateRiskType
import random


def main():
    """Run the climate insurance model simulation."""
    config = ModelConfig(
        n_households=1000,
        n_insurers=5,
        initial_insurer_capital=100000.0,
        climate_change_rate=0.01,
        grid_width=50,
        grid_height=50,
        uk_shapefile_path="data/input/Regions_Dec_2020_EN_BUC/RGN_DEC_2020_EN_BUC.shp",
        base_risk_levels={
            ClimateRiskType.FLOOD: 0.02,
            ClimateRiskType.SUBSIDENCE: 0.01,
            ClimateRiskType.STORM: 0.03,
        },
    )

    print("Initialising model")
    model = ClimateInsuranceModel(config)

    print("Running model")
    for i in range(100):
        model.step()

        if i == 50:
            print("Applying shock: 50% increase for 5 days")
            model.apply_climate_shock(
                affected_positions=[
                    (random.randint(0, 49), random.randint(0, 49)) for _ in range(25)
                ],
                shock_magnitude=1.1,
                duration=5,
            )

    print("Writing results")
    model_results = model.datacollector.get_model_vars_dataframe()
    model_results.to_excel("data/output/collector_df.xlsx")


if __name__ == "__main__":
    main()
