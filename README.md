# Telemetry Dashboard

An interactive Streamlit application for analyzing system residency telemetry data.

## 🔗 Live Demo: https://telemetry-dashboard.streamlit.app/

## Features

- **Daily Patterns**: Visualize 24-hour residency cycles with rolling averages and FFT periodograms.
- **Anomaly Detection**: Flag outliers using both a simple Z-score rule and Isolation Forest (ML).
- **Trend Reversals**: Identify trend changes with the Aroon Up/Down indicator.
- **Quick Insights**: Hero metrics and sidebar highlights surface key numbers at a glance.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Deployment](#deployment)
   - [Deploying to Heroku](#deploying-to-heroku)
   - [Deploying to Streamlit Community Cloud](#deploying-to-streamlit-community-cloud)
5. [Project Structure](#project-structure)

## Prerequisites

- Python 3.11.9  
- Git  
- A modern web browser  

## Installation

```bash
# Clone the repo
git clone https://github.com/snigdhabose/telemetry-dashboard.git
cd telemetry-dashboard

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the Streamlit app locally
streamlit run app.py
```

- Open http://localhost:8501 in your browser.  
- Select a system from the sidebar and explore metrics and plots.  

## Deployment

### Deploying to Heroku

1. Create a Heroku app:
   ```bash
   heroku create <your-app-name>
   ```
2. Push to Heroku:
   ```bash
   git push heroku main
   heroku ps:scale web=1
   heroku open
   ```

### Deploying to Streamlit Community Cloud

1. Push your code to a public GitHub repository.  
2. Go to https://share.streamlit.io and sign in.  
3. Click "New app", select your repo, branch, and `app.py` as the entry point.  
4. Click "Deploy" and share the generated URL.  

## Project Structure

```text
├── app.py
├── sample_residency_patterns.csv  # Demo telemetry dataset (10,000 records)
├── requirements.txt               # Python dependencies
├── Procfile                       # Heroku startup command
├── runtime.txt                    # Python runtime (3.11.9)
└── README.md                      # This documentation
```

---

*Feel free to open an issue if you have questions or suggestions!*
