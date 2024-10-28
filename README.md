# Climate Hackathon - 2024
Agent based model of interactions between households under climate risk and insurer capital, etc.

## Todo:
- [] Create the grid based off the UK map
- [] Put climate risks & household info the grid using input data
- [] Make agent behaviour more sophisticated (hopefully some interesting dynamics emerge!)
- [] Make climate risk dynamics more realistic (affect multiple households at a time - perhaps just allow for climate events as thing rather than risk)
- [] Create visualisations of variables such as household location, claims, capital, etc, moving through time

## Structure
model_outline.drawio.png
README.md
run.py
data
│
├── input
└── output
model
│
├── __init__.py
├── agents.py        # All agent classes
├── model.py         # Main model implementation
├── types.py         # Data classes and types
├── utils.py         # Helper functions and utilities
└── run.py          # Entry point and configuration
