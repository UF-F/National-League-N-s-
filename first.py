import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import PyPizza

st.set_page_config(page_title="Player Scout Dashboard", layout="wide")

# =============================================================================
# FILE PATHS
# =============================================================================
PER90_FILE = "National_league_players(Per90).csv"
PERCENTILE_FILE = "National_league_players(Percentile).csv"
SEASON_TOTAL_FILE = "National_league_players(Season total).csv"

per90_df = pd.read_csv(PER90_FILE)
pct_df = pd.read_csv(PERCENTILE_FILE)
season_df = pd.read_csv(SEASON_TOTAL_FILE)

per90_df.columns = per90_df.columns.str.strip()
pct_df.columns = pct_df.columns.str.strip()
season_df.columns = season_df.columns.str.strip()

# =============================================================================
# ROLE LOGIC (OUTFIELD ONLY)
# =============================================================================
def detect_role(position):
    pos = str(position).lower()

    if any(k in pos for k in ["back", "cb", "def"]):
        return "Defensive"
    elif any(k in pos for k in ["wing", "st", "cf", "am"]):
        return "Attacking"
    else:
        return "Midfield"

# =============================================================================
# METRICS BY ROLE
# =============================================================================
radar_metrics = {
    "Attacking": ["xG","Assists","Shots","Dribbles","Touches In Box","Key Passes"],
    "Midfield": ["Passing%","Key Passes","Ball Recoveries","Tack&Int","Deep Progressions"],
    "Defensive": ["Clearances","Tack&Int","Aerial Win%","Ball Recoveries","Defensive Regains"]
}

# =============================================================================
# TABS
# =============================================================================
tab1, tab2 = st.tabs(["📊 Percentile Dashboard", "👤 Player Profile Radar"])

# =============================================================================
# TAB 1 – PERCENTILE BAR DASHBOARD
# =============================================================================
with tab1:

    st.sidebar.header("Percentile Settings")

    positions = sorted(per90_df["Primary Position"].dropna().unique())
    selected_position = st.sidebar.selectbox("Filter by Position", positions)

    filtered_players = per90_df[per90_df["Primary Position"] == selected_position]["Name"].unique()
    selected_player = st.sidebar.selectbox("Choose Player", sorted(filtered_players))

    role = detect_role(selected_position)
    metrics = radar_metrics[role]

    player_row = pct_df[pct_df["Name"] == selected_player].iloc[0]
    values = [player_row[m] for m in metrics]

    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(metrics))

    ax.barh(y, values, color="black")
    ax.set_xlim(0, 100)
    ax.set_yticks(y)
    ax.set_yticklabels(metrics)
    ax.invert_yaxis()

    ax.set_title(f"{selected_player} | {role} Percentile Profile")

    st.pyplot(fig)

# =============================================================================
# TAB 2 – PLAYER RADAR
# =============================================================================
with tab2:

    st.sidebar.header("Player Radar Settings")

    player_list = sorted(per90_df["Name"].unique())
    selected_player = st.sidebar.selectbox("Choose Player", player_list)

    role_choice = st.sidebar.selectbox("Role", ["Auto", "Attacking", "Midfield", "Defensive"])

    row90 = per90_df[per90_df["Name"] == selected_player].iloc[0]
    rowpct = pct_df[pct_df["Name"] == selected_player].iloc[0]

    auto_role = detect_role(row90["Primary Position"])
    role = auto_role if role_choice == "Auto" else role_choice

    metrics = radar_metrics[role]
    values = [rowpct[m] for m in metrics]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, polar=True)

    baker = PyPizza(
        params=metrics,
        min_range=[0]*len(metrics),
        max_range=[100]*len(metrics)
    )

    baker.make_pizza(
        values,
        ax=ax,
        kwargs_slices=dict(facecolor="black"),
        kwargs_params=dict(color="black", fontsize=9),
        kwargs_values=dict(color="black", fontsize=9)
    )

    st.pyplot(fig)

