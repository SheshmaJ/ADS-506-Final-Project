"""Regional electricity demand forecast dashboard (Streamlit).

Run:  streamlit run app.py

Demo mode: with no data files, the app shows illustrative numbers.
Connect your results by adding any of these CSVs to a ./data folder:
  daily_demand.csv  -> unique_id, ds, y                     (daily average MW)
  forecasts.csv     -> unique_id, model, ds, yhat, lo_80, hi_80, lo_95, hi_95
  accuracy.csv      -> unique_id, model, MAE, RMSE
unique_id is CAL / TEX / NY; model is SNAIVE / ARIMA / ETS / TSLM.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Regional electricity demand forecast",
                   page_icon="⚡", layout="wide")

# ---------------------------------------------------------------- constants
DATA_DIR = Path(__file__).resolve().parent / "data"
TRAIN_END = pd.Timestamp("2025-09-30")
REGIONS = {"California": "CAL", "Texas": "TEX", "New York": "NY"}
MODELS = {
    "Weekly seasonal naive": "SNAIVE",
    "TSLM (trend)": "TSLM_trend",
    "TSLM (trend + weekday)": "TSLM_weekday",
    "TSLM (weekday + Fourier)": "TSLM_fourier",
}
P95_DEFAULT = {"CAL": 40428.84, "TEX": 63585.69, "NY": 22805.92}   # from training data
MEAN_DEMAND = {"CAL": 31318.82, "TEX": 46081.18, "NY": 17627.76}
Z95_OVER_Z80 = 1.96 / 1.2816
BLUE, ORANGE, RED = "#0B5CFF", "#D9480F", "#D6232A"

# Illustrative California numbers used when no data files are present
DEMO_ACTUAL = [29900, 30600, 30200, 29000, 28000, 28500, 30800, 31300, 30900, 31800,
               32800, 31200, 30400, 31900, 33500, 34600, 34100, 32800, 31600, 33800,
               35000, 35200]                                   # days -21 .. 0
DEMO_FC = [36200, 37400, 38800, 39100, 37800, 35800, 34300]
DEMO_LO80 = [35500, 36500, 37900, 37900, 36900, 33700, 32200]
DEMO_HI80 = [36900, 38300, 39700, 40900, 39400, 37900, 36400]

# --------------------------------------------------------------------- style
st.markdown("""
<style>
[data-testid="stSidebar"]{background:linear-gradient(180deg,#EEF3FC,#E8EFFA);border-right:1px solid #DCE4F2}
.side-title{font-size:26px;font-weight:700;margin:0 0 2px}
.side-h{font-size:16px;font-weight:700;margin:10px 0 0}
.main-title{font-size:38px;font-weight:700;line-height:1.1;margin:0;padding:0}
.sub{font-size:18px;color:#3A4254;margin:0 0 2px}
/* Compact KPI boxes */
.kpi {
    border: 1px solid #C9D3E3;
    border-radius: 10px;
    padding: 5px 12px;
    background: #fff;
    height: auto;
    min-height: 0;
}

.kpi .t {
    font-size: 14px;
    font-weight: 700;
    line-height: 1.2;
}

.kpi .v {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.1;
    margin: 2px 0;
}

.kpi .n {
    font-size: 12px;
    line-height: 1.2;
}
.kpi .t{font-size:16px;font-weight:700}
.kpi .v{font-size:34px;font-weight:700;line-height:1.1}
.kpi .n{font-size:14px;color:#3A4254}
.kpi.risk{background:#FDECEC;border-color:#F3B5B5}
.kpi.risk .v{color:#D0201F}
.kpi.ok{background:#EAF6EE;border-color:#B7DDC2}
.kpi.ok .v{color:#1E7A3C}
.panel-h{font-size:23px;font-weight:700;margin:0}
.panel-s{font-size:15px;color:#3A4254;margin:0 0 2px}
table.t{width:100%;border-collapse:collapse;font-size:15px}
table.t th{text-align:left;font-weight:700;border-bottom:2px solid #D5DCE8;padding:5px 8px}
table.t td{padding:4px 8px;border-bottom:1px solid #E6EAF2}
table.t tr.watch td{background:#FDECEC}
table.t .w{color:#D0201F;font-weight:700}
.note{background:#EEF1F6;border-radius:6px;padding:6px 10px;font-style:italic;font-size:15px;color:#3A4254;margin-top:6px}
div.stButton>button[kind="primary"]{background:#D6232A;border:0;color:#fff;font-weight:700;font-size:19px;padding:.55rem 1rem}
div.stButton>button[kind="primary"]:hover{background:#B81D23;color:#fff}
[data-testid="stDownloadButton"] button{background:#fff;border:1px solid #9AA6BB;color:#1B1F2A}
[data-testid="stSlider"] [role="slider"]{background:#D6232A}
.stTabs [data-baseweb="tab-list"]{gap:8px;border-bottom:2px solid #D5DCE8}
.stTabs [data-baseweb="tab"]{padding:4px 16px}
.stTabs [data-baseweb="tab"] p{font-size:17px}
.stTabs [aria-selected="true"]{background:#0F7F7B;border-radius:6px 6px 0 0}
.stTabs [aria-selected="true"] p{color:#fff}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#C9D3E3;border-radius:10px}
[data-testid="stHeader"]{display:none}
[data-testid="stMainBlockContainer"] {
    padding-top: 0rem !important;
    padding-bottom: 0.4rem !important;
    max-width: 100% !important;
}
.block-container [data-testid="stVerticalBlock"]{gap:.45rem}
[data-testid="stSidebarHeader"]{display:none}
[data-testid="stSidebarUserContent"]{padding-top:.8rem}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:0.65rem}
[data-testid="stVerticalBlockBorderWrapper"]{padding:.4rem .8rem!important}
/* push main heading up */
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"]{padding-top:0!important}
.main-title{margin-top:-1rem!important;line-height:1.15}

/* stop subtitle text from touching the boxes below */
.sub{line-height:1.5;margin:0 0 .6rem!important;padding-bottom:2px}
.panel-h{line-height:1.3}
.panel-s{line-height:1.5;margin:0 0 .6rem!important}

/* a little more breathing room between rows */
.block-container [data-testid="stVerticalBlock"]{gap:.7rem}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------- data
@st.cache_data
def load_csv(name: str):
    path = DATA_DIR / name
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if "ds" in df.columns:
        df["ds"] = pd.to_datetime(df["ds"])
    return df


def demo_history(code: str, days: int = 1095) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    idx = pd.date_range(end=TRAIN_END, periods=days)
    season = np.cos((idx.dayofyear.values - 205) / 365.25 * 2 * np.pi)
    weekly = np.where(idx.dayofweek >= 5, -0.03, 0.01)
    trend = np.linspace(-0.12, 0.12, days) if code == "TEX" else 0
    mean = MEAN_DEMAND[code]
    y = mean * (1 + 0.18 * season + weekly + trend) + rng.normal(0, 0.03 * mean, days)
    return pd.DataFrame({"ds": idx, "y": y})


def get_history(code: str) -> pd.DataFrame:
    daily = load_csv("daily_demand.csv")
    if daily is not None:
        sub = daily[daily["unique_id"] == code][["ds", "y"]].sort_values("ds")
        if len(sub):
            return sub.reset_index(drop=True)
    return demo_history(code)


def get_view(code: str, model: str, horizon: int):
    """Return recent actuals, forecast table, P95 threshold, and demo flag."""
    hist = get_history(code)
    daily = load_csv("daily_demand.csv")
    p95 = P95_DEFAULT[code]
    if daily is not None:
        train = hist[hist["ds"] <= TRAIN_END]["y"].dropna()
        if len(train):
            p95 = float(train.quantile(0.95))
    fcs = load_csv("forecasts.csv")
    if fcs is not None:
        f = fcs[(fcs["unique_id"] == code) & (fcs["model"] == model)].sort_values("ds")
        if len(f):
            f = f.head(horizon).reset_index(drop=True)
            recent = hist["y"].ffill().tail(22).to_numpy()
            out = pd.DataFrame({"Day": np.arange(1, len(f) + 1), "yhat": f["yhat"],
                                "lo80": f["lo_80"], "hi80": f["hi_80"],
                                "lo95": f["lo_95"], "hi95": f["hi_95"]})
            return recent, out, p95, False
    k = MEAN_DEMAND[code] / MEAN_DEMAND["CAL"]
    yhat = np.array(DEMO_FC) * k
    lo80, hi80 = np.array(DEMO_LO80) * k, np.array(DEMO_HI80) * k
    out = pd.DataFrame({"Day": np.arange(1, 8), "yhat": yhat, "lo80": lo80, "hi80": hi80,
                        "lo95": yhat - Z95_OVER_Z80 * (yhat - lo80),
                        "hi95": yhat + Z95_OVER_Z80 * (hi80 - yhat)}).head(horizon)
    return np.array(DEMO_ACTUAL) * k, out, p95, True


def get_accuracy(code: str):
    acc = load_csv("accuracy.csv")

    if acc is None:
        st.error(f"Accuracy file not found: {DATA_DIR / 'accuracy.csv'}")
        return None

    acc.columns = acc.columns.str.strip()

    required = {"unique_id", "model", "MAE", "RMSE"}
    if not required.issubset(acc.columns):
        st.error(f"Accuracy CSV columns: {acc.columns.tolist()}")
        return None

    acc["unique_id"] = acc["unique_id"].astype(str).str.strip().str.upper()
    acc["model"] = acc["model"].astype(str).str.strip()

    model_mapping = {
        "SNAIVE": "SNAIVE",
        "Weekly seasonal naive": "SNAIVE",
        "TSLM_trend": "TSLM_trend",
        "TSLM_weekday": "TSLM_weekday",
        "TSLM_fourier": "TSLM_fourier",
    }

    acc["model"] = acc["model"].replace(model_mapping)

    for col in ["MAE", "RMSE"]:
        acc[col] = pd.to_numeric(
            acc[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    sub = acc[acc["unique_id"] == code].copy()

    if sub.empty:
        st.warning(f"No accuracy results for {code}")
        st.write("Available regions:", acc["unique_id"].unique().tolist())
        return None

    return sub


# ------------------------------------------------------------------- helpers

def show_chart(fig):
    """Full-width Plotly chart that works on old and new Streamlit versions."""
    cfg = {"displayModeBar": False}
    try:
        st.plotly_chart(fig, width="stretch", config=cfg)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config=cfg)

def fmt(v) -> str:
    return f"{v:,.0f}"


def kpi(title, value, note, cls=""):
    return (f'<div class="kpi {cls}"><div class="t">{title}</div>'
            f'<div class="v">{value}</div><div class="n">{note}</div></div>')


def forecast_chart(recent, fc, p95, show80, show95, show_p95):
    n = len(recent)
    x_hist = np.arange(-(n - 1), 1)
    x_fc = np.concatenate([[0], fc["Day"].to_numpy()])
    last = recent[-1]
    line = lambda col: np.concatenate([[last], fc[col].to_numpy()])
    fig = go.Figure()
    for show, lo, hi, color, name in [(show95, "lo95", "hi95", "#FCE6D4", "95% range"),
                                      (show80, "lo80", "hi80", "#F8C9A3", "80% range")]:
        if show:
            fig.add_trace(go.Scatter(x=np.concatenate([x_fc, x_fc[::-1]]),
                                     y=np.concatenate([line(hi), line(lo)[::-1]]),
                                     mode="lines", fill="toself", fillcolor=color, line=dict(width=0),
                                     hoverinfo="skip", name=name))
    fig.add_trace(go.Scatter(x=x_hist, y=recent, mode="lines", name="Actual",
                             line=dict(color=BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=x_fc, y=line("yhat"), mode="lines", name="Forecast",
                             line=dict(color=ORANGE, width=3)))
    ymax_data = max([p95 if show_p95 else 0, fc["hi80"].max(), np.max(recent)])
    lo_axis = np.floor((min(np.min(recent), fc["lo80"].min()) - 1500) / 2000) * 2000
    hi_axis = np.ceil((ymax_data + 1000) / 2000) * 2000
    step = max(1000, round((hi_axis - lo_axis) / 4 / 1000) * 1000)
    ticks = np.arange(lo_axis, hi_axis + 1, step)
    if show_p95:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="P95 threshold",
                                 line=dict(color="#111", dash="dash", width=1.5)))
        fig.add_hline(y=p95, line_dash="dash", line_color="#111", line_width=1.5,
                      annotation_text=f"P95 {fmt(p95)} MW", annotation_position="top right")
    fig.add_vline(x=0, line_dash="dot", line_color="#777", annotation_text="Forecast origin",
                  annotation_position="bottom left")
    shown = [-21, -14, -7, 0, 3, 7]
    fig.update_layout(
        height=280, margin=dict(l=70, r=20, t=38, b=30), plot_bgcolor="white",
        font=dict(family="Source Serif 4, Georgia, serif", size=15, color="#1B1F2A"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
        xaxis=dict(tickvals=shown, ticktext=["−21d", "−14d", "−7d", "Today", "+3d", "+7d"],
                   showgrid=False, linecolor="#1B1F2A"),
        yaxis=dict(title="Daily average demand (MW)", range=[lo_axis, hi_axis],
                   tickvals=ticks, ticktext=[f"{t / 1000:.0f}k" for t in ticks],
                   gridcolor="#E6EAF2", linecolor="#1B1F2A"))
    return fig


def forecast_table_html(fc, p95):
    rows = ""
    for _, r in fc.iterrows():
        watch = r["hi95"] >= p95
        risk = '<span class="w">Watch</span>' if watch else "Low"
        rows += (f'<tr class="{"watch" if watch else ""}"><td>+{int(r.Day)}</td>'
                 f'<td>{fmt(r.yhat)}</td><td>{fmt(r.lo80)} to {fmt(r.hi80)}</td>'
                 f'<td>{risk}</td></tr>')
    return ('<table class="t"><tr><th>Day</th><th>Forecast (MW)</th><th>80% range</th>'
            f'<th>Risk</th></tr>{rows}</table>')


def accuracy_html(acc):
    best = {}
    if acc is not None:
        for m in ("MAE", "RMSE"):
            best[m] = acc[m].min()
    rows = ""
    for label, code in MODELS.items():
        vals = ["—", "—"]
        if acc is not None and (acc["model"] == code).any():
            r = acc[acc["model"] == code].iloc[0]
            vals = [(f"<b>{fmt(r[m])}</b>" if r[m] == best[m] else fmt(r[m]))
                    for m in ("MAE", "RMSE")]
        rows += f"<tr><td>{label}</td><td>{vals[0]}</td><td>{vals[1]}</td></tr>"
    return ('<table class="t"><tr><th>Model</th><th>MAE</th><th>RMSE</th></tr>'
            f'{rows}</table>')


# ------------------------------------------------------------------- sidebar
sb = st.sidebar
sb.markdown('<div class="side-title">Forecast settings</div>', unsafe_allow_html=True)
sb.markdown('<div class="side-h">Region</div>', unsafe_allow_html=True)
sb.caption("Choose the region to explore.")
picked = [name for name, default in zip(REGIONS, (True, False, False))
          if sb.checkbox(name, value=default, key=f"region_{name}")]
sb.markdown('<div class="side-h">Forecast horizon (days ahead)</div>', unsafe_allow_html=True)
sb.caption("Choose how many days ahead to predict.")
horizon = sb.slider("Horizon", 1, 7, 7, label_visibility="collapsed")
sb.markdown('<div class="side-h">Models</div>', unsafe_allow_html=True)
sb.caption("Choose models to compare.")
chosen = [label for label in MODELS if sb.checkbox(label, value=True, key=f"model_{label}")]
sb.markdown('<div class="side-h">Prediction interval</div>', unsafe_allow_html=True)
sb.caption("Show a range of possible demand values.")
show80 = sb.checkbox("80% interval", value=True)
show95 = sb.checkbox("95% interval", value=True)
show_p95 = sb.checkbox("Show high-demand threshold (P95)", value=True)
sb.caption("Mark unusually high demand using the training data.")
try:
    run = sb.button("Run forecast", type="primary", width="stretch")
except TypeError:
    run = sb.button("Run forecast", type="primary", use_container_width=True)
if run:
    st.cache_data.clear()
    st.toast("Forecast refreshed")

if not picked or not chosen:
    st.info("Select at least one region and one model in the sidebar.")
    st.stop()
if len(picked) > 1:
    sb.caption(f"Showing {picked[0]} (first selected region).")

region = picked[0]
code = REGIONS[region]
model_label = chosen[0]
recent, fc, p95, is_demo = get_view(code, MODELS[model_label], horizon)
acc = get_accuracy(code)
st.sidebar.write("Accuracy file exists:", (DATA_DIR / "accuracy.csv").exists())
st.sidebar.write("Selected region:", code)
st.sidebar.write("Accuracy rows:", 0 if acc is None else len(acc))

if acc is not None:
    st.sidebar.write("Models found:", acc["model"].tolist())
# ---------------------------------------------------------------------- main
st.markdown('<h1 class="main-title">Regional electricity demand forecast</h1>',
            unsafe_allow_html=True)
st.markdown(f'<div class="sub">Compare regional demand and forecast the next {horizon} days.</div>',
            unsafe_allow_html=True)

labels = ["Demand history", "Forecast comparison", "Model accuracy", "About"]
try:
    tabs = st.tabs(labels, default="Forecast comparison")   # newer Streamlit
except TypeError:
    tabs = st.tabs(labels)
t_hist, t_fc, t_acc, t_about = tabs

with t_hist:
    st.caption("See how demand changes over time and by season.")
    h = get_history(code)
    h = h.tail(1095)
    fig = go.Figure(go.Scatter(x=h["ds"], y=h["y"], mode="lines", line=dict(color=BLUE, width=1.6)))
    fig.update_layout(height=340, margin=dict(l=60, r=20, t=20, b=40), plot_bgcolor="white",
                      yaxis=dict(title="Daily average demand (MW)", gridcolor="#E6EAF2"))
    show_chart(fig)
    monthly = h.assign(m=h["ds"].dt.month).groupby("m")["y"].mean()
    fig2 = go.Figure(go.Bar(x=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                               "Oct", "Nov", "Dec"], y=monthly.reindex(range(1, 13)).to_numpy(),
                            marker_color="#0F7F7B"))
    fig2.update_layout(height=280, margin=dict(l=60, r=20, t=30, b=40), plot_bgcolor="white",
                       title="Average demand by month",
                       yaxis=dict(title="MW", gridcolor="#E6EAF2"))
    show_chart(fig2)

with t_fc:
    st.markdown('<div class="sub">Compare predicted demand with recent actual demand and '
                'see the uncertainty.</div>', unsafe_allow_html=True)
    peak = fc["yhat"].max()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Next-day forecast", f"{fmt(fc['yhat'].iloc[0])} MW",
                    "Expected demand tomorrow."), unsafe_allow_html=True)
    c2.markdown(kpi(f"{horizon}-day peak forecast", f"{fmt(peak)} MW",
                    "Highest predicted demand this week."), unsafe_allow_html=True)
    c3.markdown(kpi("High-demand threshold (P95)", f"{fmt(p95)} MW",
                    "Demand exceeded on 5% of training days."), unsafe_allow_html=True)
    if (fc["hi95"] >= p95).any():
        c4.markdown(kpi("High-demand risk", "Watch", "The upper prediction range crosses "
                        "the threshold.", "risk"), unsafe_allow_html=True)
    else:
        c4.markdown(kpi("High-demand risk", "Low", "The prediction range stays below "
                        "the threshold.", "ok"), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="panel-h">Recent demand and {horizon}-day forecast</div>'
                    f'<div class="panel-s">Blue shows recorded demand. Orange shows the '
                    f'{model_label} forecast; shaded bands show uncertainty.</div>',
                    unsafe_allow_html=True)
        show_chart(forecast_chart(recent, fc, p95, show80, show95, show_p95))

    left, right = st.columns(2)
    with left, st.container(border=True):
        st.markdown(f'<div class="panel-h">{horizon}-day forecast table</div>'
                    '<div class="panel-s">Check daily forecasts and download the results.</div>',
                    unsafe_allow_html=True)
        st.markdown(forecast_table_html(fc, p95), unsafe_allow_html=True)
        export = fc.rename(columns={"yhat": "Forecast (MW)", "lo80": "80% low", "hi80": "80% high",
                                    "lo95": "95% low", "hi95": "95% high"}).round(0)
        export["Risk"] = np.where(fc["hi95"] >= p95, "Watch", "Low")
        st.download_button("Download forecast (CSV)", export.to_csv(index=False),
                           file_name=f"forecast_{code}.csv", mime="text/csv")
    with right, st.container(border=True):
        st.markdown('<div class="panel-h">Model accuracy</div><div class="panel-s">Compare errors on '
                    'past forecast windows. Lower MAE and RMSE are better.</div>',
                    unsafe_allow_html=True)
        st.markdown(accuracy_html(acc), unsafe_allow_html=True)
        if acc is None:
            st.markdown('<div class="note">Calculated from project results when connected.</div>',
                        unsafe_allow_html=True)

with t_acc:
    st.markdown(f'<div class="panel-h">Model accuracy: {region}</div>'
                '<div class="panel-s">Errors on past forecast windows. Lower is better.</div>',
                unsafe_allow_html=True)
    st.markdown(accuracy_html(acc), unsafe_allow_html=True)
    if acc is None:
        st.markdown('<div class="note">Add data/accuracy.csv to show cross-validation results.</div>',
                    unsafe_allow_html=True)

with t_about:
    st.markdown("""
**Data.** Hourly electricity demand from the U.S. Energy Information Administration (EIA-930) for
California, Texas, and New York, averaged to one value per day (MW).

**Models.** Weekly seasonal naive (baseline), ARIMA, ETS, and time series linear regression with
weekday and Fourier terms.

**Evaluation.** Rolling-origin cross-validation on the training period (July 2015 to September 2025)
and a separate holdout year (October 2025 to September 2026). The high-demand threshold is each
region's 95th-percentile daily demand in the training period.

**Limits.** The models use only past demand and calendar patterns, with no weather inputs.
""")
