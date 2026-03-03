import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import PyPizza

st.set_page_config(page_title="Player Scout Dashboard", layout="wide")

# =============================================================================
# LOAD DATA
# =============================================================================
PER90_FILE = "National_league_players (Per90).csv"
PERCENTILE_FILE = "National_league_players(Percentile).csv"
SEASON_TOTAL_FILE = "National_league_players(Season total).csv"

per90_df = pd.read_csv(PER90_FILE)
pct_df = pd.read_csv(PERCENTILE_FILE)
season_df = pd.read_csv(SEASON_TOTAL_FILE)

for df in [per90_df, pct_df, season_df]:
    df.columns = df.columns.str.strip()

# =============================================================================
# ROLE DETECTION (OUTFIELD ONLY)
# =============================================================================
def detect_role(position):
    pos = str(position).lower()

    if any(k in pos for k in ["cb", "back", "def"]):
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
tab1, tab2 = st.tabs(["📊 Percentile Dashboard", "👤 Player Radar"])

# =============================================================================
# TAB 1 – PLAYER PERCENTILE DASHBOARD
# =============================================================================
with tab1:

    st.sidebar.header("Player Selection")

    positions = sorted(per90_df["Primary Position"].dropna().unique())
    selected_position = st.sidebar.selectbox("Position", positions)

    players = per90_df[
        per90_df["Primary Position"] == selected_position
    ]["Name"].unique()

    selected_player = st.sidebar.selectbox("Player", sorted(players))

    role = detect_role(selected_position)
    metrics = radar_metrics[role]

    player_row = pct_df[pct_df["Name"] == selected_player].iloc[0]
    values = [player_row[m] for m in metrics]

    team_name = season_df[
        season_df["Name"] == selected_player
    ]["Team"].iloc[0]

    # Styling
    BG = "#F5F1E6"
    GREEN = "#008000"
    RED = "#A52A2A"

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    y = np.arange(len(metrics))
    colors = [GREEN if v >= 50 else RED for v in values]

    ax.barh(y, values, color=colors, edgecolor="black")

    # Value labels
    for i, v in enumerate(values):
        ax.text(v + 1, i, f"{v:.1f}", va="center", fontsize=11)

    ax.set_xlim(0, 100)
    ax.set_yticks(y)
    ax.set_yticklabels(metrics, fontsize=12)
    ax.invert_yaxis()

    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    for spine in ax.spines.values():
        spine.set_visible(False)

    # Titles
    fig.text(0.125, 0.94,
             f"{selected_player} | {team_name}",
             fontsize=20,
             weight="bold")

    fig.text(0.125, 0.91,
             "Percentile Rank National League North/South | Season 2025-26",
             fontsize=12)

    fig.text(0.125, 0.885,
             "Data: StatsBomb | Graphic: @Neil_barretto",
             fontsize=10,
             color="gray")

    st.pyplot(fig)

# =============================================================================
# TAB 2 – PLAYER RADAR (MPLSOCCER STYLE)
# =============================================================================
with tab2:

    st.sidebar.header("Radar Settings")

    player_list = sorted(per90_df["Name"].unique())
    selected_player = st.sidebar.selectbox("Select Player", player_list)

    role_choice = st.sidebar.selectbox(
        "Role",
        ["Auto", "Attacking", "Midfield", "Defensive"]
    )

    row90 = per90_df[per90_df["Name"] == selected_player].iloc[0]
    rowpct = pct_df[pct_df["Name"] == selected_player].iloc[0]

    auto_role = detect_role(row90["Primary Position"])
    role = auto_role if role_choice == "Auto" else role_choice

    metrics = radar_metrics[role]
    values = [rowpct[m] for m in metrics]

    baker = PyPizza(
        params=metrics,
        background_color="#F5F1E6",
        straight_line_color="#DDDDDD",
        straight_line_lw=1,
        last_circle_lw=1,
        other_circle_lw=0,
        min_range=[0]*len(metrics),
        max_range=[100]*len(metrics)
    )

    fig, ax = baker.make_pizza(
        values,
        figsize=(8, 8),
        slice_colors=["#1A1A1A"] * len(metrics),
        value_colors=["#1A1A1A"] * len(metrics),
        value_bck_colors=["#F2F2F2"] * len(metrics),
        blank_alpha=0.4,
        kwargs_slices=dict(edgecolor="#000000", linewidth=1),
        kwargs_params=dict(color="#000000", fontsize=11),
        kwargs_values=dict(color="#000000", fontsize=10)
    )

    team_name = season_df[
        season_df["Name"] == selected_player
    ]["Team"].iloc[0]

    fig.text(0.5, 0.95,
             f"{selected_player} | {team_name}",
             size=18,
             ha="center",
             weight="bold")

    fig.text(0.5, 0.91,
             f"{role} Profile | National League N/S 2025-26",
             size=12,
             ha="center",
             color="#444444")

    st.pyplot(fig)
