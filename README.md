

# ADS-506: Regional Short-Term Electricity Demand Forecasting

**Project Team:** Team 4 

**Team Members**: Sheshma Jaganathan, Caly Nguyen, Harshali Gaikwad

**Course:** ADS-506 – Time Series Analysis and Forecasting  

## Project Overview

This project focuses on forecasting daily average electricity demand (MW) for California (CAL), Texas (TEX), and New York (NY) using historical electricity demand data from the U.S. Energy Information Administration (EIA).

The goal is to forecast electricity demand for the next 7 days (Days 1–7) and compare different time series forecasting models to identify the most accurate methods for each region.

## Business Problem

Electricity demand changes by day of the week and season, making energy planning challenging. Accurate short-term forecasts can help electricity providers prepare for changes in demand, improve resource planning, and manage high-demand periods.

## Research Questions

1. How do trends and seasonal patterns differ across California, Texas, and New York?
2. How do Seasonal Naïve, ETS, ARIMA, TSLM, and dynamic regression models compare in forecasting accuracy?
3. Do calendar and Fourier predictors improve forecasting performance?
4. How accurately do the models predict high-demand days?

## Dataset

**Source:** [U.S. Energy Information Administration (EIA) – Electricity Grid Monitor](https://www.eia.gov/electricity/gridmonitor/)

| Column | Purpose |
|---|---|
| Region | Identify California, Texas or New York |
| Local date | Aggregate hourly demand into daily observations |
| UTC time | Check duplicates, missing hours and daylight saving time |
| Demand | Actual demand in MW (the forecasting target) |
| Time zone | Verify local-time handling per region |


## Tools and Libraries

- Python
- VS Code
- Quarto and Jupyter
- pandas and NumPy
- Matplotlib
- statsmodels
- fpppy
- statsforecast

## Project Workflow

1. **Data Preparation:** Clean and combine the three regional datasets.
2. **Exploratory Data Analysis:** Examine demand trends, seasonality, and unusual values.
3. **Time Series Analysis:** Apply decomposition, stationarity tests, and transformations.
4. **Model Development:** Fit and compare Seasonal Naïve, ETS, ARIMA, TSLM, and dynamic regression models.
5. **Cross-Validation:** Evaluate forecasting accuracy using rolling-origin cross-validation.
6. **Holdout Evaluation:** Assess selected models using unseen data.
7. **Results:** Compare model performance across regions, forecast horizons, and high-demand periods.

## Repository Layout

```
ADS-506-Final-Project/
├── README.md
├── requirements.txt
├── data/                    # EIA-930 Excel datasets
│   ├── Region_CAL.xlsx
│   ├── Region_TEX.xlsx
│   └── Region_NY.xlsx
├── notebook/                # Python Quarto files
│   └── ADS506_Final_Project_team4.qmd
├── docs/                    # Project documentation
│   ├── Final_Report.pdf
│   └── Final_Presentation.pptx
└── .gitignore

```

## How to Run the Project

**1. Clone the repository**

```bash
git clone https://github.com/SheshmaJ/ADS-506-Final-Project.git
```

**2. Open the project in VS Code**

Install Python, Quarto, and the Python, Jupyter, and Quarto VS Code extensions.

**3. Install required libraries**

```bash
py -m pip install -r requirements.txt
```

Use the same Python environment for package installation and the Jupyter kernel.

**4. Run the analysis**

Open `notebook/ADS506_Final_Project_team4.qmd` in VS Code.

Confirm the data paths, select the Python kernel, and run the code cells in order. The report can also be rendered using Quarto.

## Team Contribution Summary

**Sheshma Jaganathan**: Data preparation, preprocessing, initial exploratory data analysis, and evaluation setup.

**Caly Nguyen**: Time series decomposition, feature engineering, additional exploratory analysis, transformations, and diagnostics.

**Harshali Gaikwad**: Forecasting model development, cross-validation, model comparison, holdout evaluation, and final results.

Note: All team members will work collaboratively on the final project report and presentation, including reviewing results, making improvements, and preparing the final deliverables.

## Reference

U.S. Energy Information Administration (EIA). [Electricity Grid Monitor](https://www.eia.gov/electricity/gridmonitor/).
