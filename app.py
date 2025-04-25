# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest

# — INITIAL SETUP —
st.set_page_config(page_title="Telemetry Dashboard", layout="wide")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["Timestamp"])
    df.set_index("Timestamp", inplace=True)
    return df

def compute_aroon(series, window):
    vals = series.values
    up = np.full(len(vals), np.nan)
    down = np.full(len(vals), np.nan)
    for i in range(window, len(vals)):
        w = vals[i - window + 1 : i + 1]
        idx_max, idx_min = w.argmax(), w.argmin()
        up[i]   = 100 * (window - 1 - idx_max) / window
        down[i] = 100 * (window - 1 - idx_min) / window
    return pd.Series(up, index=series.index), pd.Series(down, index=series.index)

# — LOAD & SELECT SYSTEM —
df = load_data("sample_residency_patterns.csv")
systems = df["System"].unique()
system = st.sidebar.selectbox("Select a system", systems)

ts = df[df["System"] == system]["Residency"].asfreq("min").interpolate()

# — METRICS COMPUTATION —
# Z-score anomalies
z = (ts - ts.mean()) / ts.std()
out_z = z.abs() > 3

# Isolation Forest anomalies
iso = IsolationForest(contamination=0.01, random_state=42)
preds = iso.fit_predict(ts.values.reshape(-1, 1))
out_ml = preds == -1

# Overlap
overlap = (out_z & out_ml).sum()

# FFT for daily period
demeaned = ts - ts.mean()
fft_vals = np.fft.rfft(demeaned)
freqs    = np.fft.rfftfreq(len(demeaned), d=1)
# ignore zero
idx = np.argmax(np.abs(fft_vals[1:])) + 1
period_minutes = 1 / freqs[idx]
period_hours   = period_minutes / 60

# Peak/trough times by hour-of-day average
hourly = ts.groupby(ts.index.hour).mean()
peak_hour   = hourly.idxmax()
trough_hour = hourly.idxmin()

# Trend reversals (Aroon crossovers)
a_up, a_down = compute_aroon(ts, window=1440)
cross_up = ((a_up > a_down) & (a_up.shift(1) <= a_down.shift(1))).sum()

# — HERO METRICS —
col1, col2, col3, col4 = st.columns(4)
col1.metric("Z-score Anomalies", int(out_z.sum()))
col2.metric("ML Anomalies", int(out_ml.sum()))
col3.metric("Shared Anomalies", int(overlap))
col4.metric("Daily Cycle (hrs)", f"{period_hours:.1f}")

# — SIDEBAR HIGHLIGHTS —
st.sidebar.markdown("### ⚡ Highlights")
st.sidebar.markdown(f"- **Mean Residency:** {ts.mean():.1f}%")
st.sidebar.markdown(f"- **Peak Time:** ~{peak_hour:02d}:00")
st.sidebar.markdown(f"- **Trough Time:** ~{trough_hour:02d}:00")
st.sidebar.markdown(f"- **Anomaly Rate (Z-score):** {out_z.mean()*100:.1f}%")
st.sidebar.markdown(f"- **Anomaly Rate (ML):** {out_ml.mean()*100:.1f}%")
st.sidebar.markdown(f"- **Trend Reversals/day:** {cross_up}")

# — CHARTS GRID —
st.subheader(f"System: {system}")

# 1) Raw vs Rolling Mean
rolling = ts.rolling(60, min_periods=1).mean()
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=ts.index, y=ts,   mode="lines", name="Raw", opacity=0.6))
fig1.add_trace(go.Scatter(x=rolling.index, y=rolling, mode="lines", name="60-min MA", line=dict(width=2)))
fig1.update_layout(title="Residency Over Time", yaxis_title="Residency (%)")

# 2) Periodogram
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=freqs, y=np.abs(fft_vals), mode="lines"))
fig2.update_layout(title="Periodogram (FFT)", xaxis_title="Freq (cycles/min)")

# 3) Z-score Anomalies
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=ts.index, y=ts, mode="lines", name="Residency"))
fig3.add_trace(go.Scatter(x=ts.index[out_z], y=ts[out_z], mode="markers",
                          name="Z-score Outlier", marker=dict(color="red", size=6)))
fig3.update_layout(title="Z-score Anomaly Detection")

# 4) ML Anomalies
fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=ts.index, y=ts, mode="lines", name="Residency"))
fig4.add_trace(go.Scatter(x=ts.index[out_ml], y=ts[out_ml], mode="markers",
                          name="ML Outlier", marker=dict(color="purple", size=6)))
fig4.update_layout(title="ML-Based Anomaly Detection")

# 5) Aroon Up/Down
fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=a_up.index, y=a_up, mode="lines", name="Aroon Up"))
fig5.add_trace(go.Scatter(x=a_down.index, y=a_down, mode="lines", name="Aroon Down"))
fig5.update_layout(title="Trend Reversals (Aroon)", yaxis_title="Aroon %")

# Display in grid
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)
with col2:
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)
st.plotly_chart(fig5, use_container_width=True)

# — SHORT INSIGHTS —
st.markdown("### Quick Takeaways")
st.markdown("""
- The residency data follows a **clear 24-hour cycle** (~{:.1f} hrs).  
- **{}** Z-score anomalies vs **{}** ML anomalies; **{}** of them overlap.  
- Peak residency around **{:02d}:00**, trough around **{:02d}:00**.  
- Detected **{}** trend reversals in the last window.  
""".format(period_hours, int(out_z.sum()), int(out_ml.sum()), int(overlap),
           peak_hour, trough_hour, cross_up))
