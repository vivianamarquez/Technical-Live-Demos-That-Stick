# From Code to Connection: How to Deliver Technical Live Demos That Stick

Materials from the talk presented at [The Content Playbook: Smarter Data, AI, Global Docs](https://luma.com/1k8djkt9?tk=UNAghJ) on January 22, 2026.

## About the Talk

Live demos can be one of the most powerful ways to teach technical concepts, when they're done well. But they can also quickly overwhelm, bore, or lose an audience if the storytelling isn't intentional. This talk presents a practical framework for crafting engaging technical learning experiences using tools like **Jupyter** and **RISE** to turn code into a compelling narrative instead of a wall of text.

## What's in This Repository

This repository contains:

- **[LiveDemos.ipynb](LiveDemos.ipynb)**: The complete interactive presentation notebook demonstrating the live demo framework
- **[prolific_helpers.py](prolific_helpers.py)**: Helper functions for interacting with the Prolific API and visualizing survey data
- **[config.yaml](config.yaml)**: Configuration file for study parameters and settings
- **[environment.yml](environment.yml)**: Conda environment specification for easy setup
- **[.env.example](.env.example)**: Template for environment variables (API keys, etc.)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/vivianamarquez/Technical-Live-Demos-That-Stick.git
cd Technical-Live-Demos-That-Stick
```

### 2. Create the Conda Environment

```bash
conda env create -f environment.yml
conda activate rise_slides
```

### 3. Run the Notebook

```bash
jupyter notebook 
```

## Using RISE for Interactive Slideshows

RISE turns Jupyter notebooks into interactive slideshows where you can run code live during presentations.

To view as a slideshow using RISE, open the notebook and click the presentation icon in the toolbar.

**Documentation**: https://rise.readthedocs.io/

## Contact

**Viviana Márquez**
AI Developer Relations Engineer @ Prolific

- 💼 LinkedIn: [/in/vivianamarquez](https://www.linkedin.com/in/vivianamarquez)
- 🐙 GitHub: [@vivianamarquez](https://github.com/vivianamarquez)
- 🌐 Prolific: [prolific.com](https://www.prolific.com)

