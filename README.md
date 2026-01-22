# From Code to Connection: How to Deliver Technical Live Demos That Stick

Materials from the talk presented at [The Content Playbook: Smarter Data, AI, Global Docs](https://luma.com/1k8djkt9?tk=UNAghJ) on January 22, 2026.

## About the Talk

Live demos can be one of the most powerful ways to teach technical concepts, when they're done well. But they can also quickly overwhelm, bore, or lose an audience if the storytelling isn't intentional. This talk presents a practical framework for crafting engaging technical learning experiences using tools like Jupyter and RISE to turn code into a compelling narrative instead of a wall of text.

## What's in This Repository

This repository contains:

- **[LiveDemos.ipynb](LiveDemos.ipynb)**: The complete interactive presentation notebook demonstrating the live demo framework
- **[prolific_helpers.py](prolific_helpers.py)**: Helper functions for interacting with the Prolific API and visualizing survey data
- **[config.yaml](config.yaml)**: Configuration file for study parameters and settings
- **[environment.yml](environment.yml)**: Conda environment specification for easy setup
- **[.env.example](.env.example)**: Template for environment variables (API keys, etc.)

## Demo Overview

The live demo showcases:
1. Authenticating with the Prolific API
2. Creating and publishing a study with an external survey link
3. Fetching and analyzing study results
4. Merging data from Google Sheets with Prolific participant data
5. Creating interactive visualizations using Plotly

The demo uses a real example: asking participants to choose between two AI-generated slides about cats, then analyzing preferences by gender, generation, and country.

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

### 3. Configure Environment Variables

Copy the example environment file and add your Prolific API credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your:
- `PROLIFIC_API_TOKEN`
- `PROLIFIC_WORKSPACE_ID`
- `PROLIFIC_PROJECT_ID`

### 4. Update Configuration

Edit `config.yaml` to customize:
- Study parameters (name, description, privacy notice)
- Participant settings (reward, sample size, time estimates)
- External survey URL
- Google Sheets ID for results data

### 5. Run the Notebook

```bash
jupyter notebook LiveDemos.ipynb
```

To view as a slideshow using RISE, open the notebook and click the presentation icon in the toolbar.

## Framework: Three Questions for Effective Live Demos

1. **What's the need?** - Know your audience. What problem do they wake up thinking about?
2. **What's the solution?** - Show how your thing solves that specific problem. Not every feature. Just: here's your pain, here's relief.
3. **What's the next step?** - Show the most impressive part, then give them a place to go: GitHub, docs, a follow-up meeting.

## Tips for Live Coding Well

- **Prepare like it's improvised** - Practice the exact sequence. Have recovery points. Seed your randomness.
- **Narrate constantly** - Silence while typing is death. Speak your thought process out loud.
- **Fail gracefully and usefully** - If something breaks, treat it as a teaching moment. This is where live demos shine over docs.

## Using RISE for Interactive Slideshows

RISE turns Jupyter notebooks into interactive slideshows where you can run code live during presentations.

**Documentation**: https://rise.readthedocs.io/

**Tips**:
- Build incrementally using fragments strategically
- Put setup code in skipped cells and run it beforehand
- Use Markdown cells for text content

## Contact

**Viviana Márquez**
AI Developer Relations Engineer @ Prolific

- 💼 LinkedIn: [/in/vivianamarquez](https://www.linkedin.com/in/vivianamarquez)
- 🐙 GitHub: [@vivianamarquez](https://github.com/vivianamarquez)
- 🌐 Prolific: [prolific.com](https://www.prolific.com)

---

*Live demos aren't a replacement for documentation. They're how you make the content stick.*