import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import PyPizza, FontManager
import os

# ---------------- STREAMLIT PAGE SETUP ----------------
st.set_page_config(page_title="National League South Dashboard 25/26", layout="wide")

# ---------------- FILE PATHS ----------------
TEAM_FILE = "League_Team_Stats (5).csv"
PLAYER_FILE = "Daggers (Per90).csv"
PLAYER_PCT_FILE = "Daggers (Percentile).csv"
OUTPUT_FOLDER = "outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------- LOAD DATA ----------------
team_df = pd.read_csv(TEAM_FILE)
team_df.columns = team_df.columns.str.strip()

player_df = pd.read_csv(PLAYER_FILE)
player_df.columns = player_df.columns.str.strip()

player_pct_df = pd.read_csv(PLAYER_PCT_FILE)
player_pct_df.columns = player_pct_df.columns.str.strip()

# ---------------- FONT ----------------
title_font = FontManager(
    "https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf"
)

# ---------------- POSITION → ROLE LOGIC (AUTO WORKS FOR BIG DATASETS) ----------------
def detect_role(primary_pos, secondary_pos=None):
    positions = []
    if pd.notna(primary_pos):
        positions.append(str(primary_pos))
    if secondary_pos is not None and pd.notna(secondary_pos):
        positions.append(str(secondary_pos))

    pos_text = " | ".join(positions).lower()

    # GK
    if "keeper" in pos_text or "goal" in pos_text:
        return "Goalkeeper"

    # Defensive
    defensive_keywords = [
        "centre back", "center back", "cb",
        "left back", "right back", "full back",
        "wing back", "wb",
        "defensive", "dm", "holding",
        "back"
    ]
    if any(k in pos_text for k in defensive_keywords):
        return "Defensive"

    # Attacking
    attacking_keywords = [
        "forward", "striker", "cf", "st",
        "wing", "rw", "lw",
        "attacking", "am", "10"
    ]
    if any(k in pos_text for k in attacking_keywords):
        return "Attacking"

    # Default
    return "Midfield"


# ---------------- TEAM DASHBOARD METRICS ----------------
team_metrics = [
    "Goals", "NP xG", "Shots", "SP xG", "Corner xG",
    "Passes Inside Box", "Successful Box Cross%", "Dribble%", "Deep Progressions",
    "Possession%", "Passing%", "PPDA", "Aggression", "Counterpressures",
    "Goals Conceded", "NP xG Against", "SP xG Against", "Corner xG Against"
]

league_row = team_df[team_df["Team Name"] == "League Average"].iloc[0]
team_names = sorted(team_df[team_df["Team Name"] != "League Average"]["Team Name"].unique())


# ---------------- PLAYER DASHBOARD METRICS ----------------
radar_metrics = {
    "Attacking": ["xG","Shooting%","Assists","xG Assisted","Key Passes",
                  "Dribbles","Successful Dribbles","Dribble%","Touches In Box",
                  "Successful Box Cross%","Crossing%","OP F3 Passes","Deep Progressions"],

    "Midfield": ["Passing%","Carry%","Dribbles","Successful Dribbles",
                 "Key Passes","Turnovers","Dispossessed",
                 "Counterpressures","Counterpress Regains",
                 "Ball Recoveries","Tack&Int","Aggressive Actions"],

    "Defensive": ["Clearances","Aggressive Actions","Defensive Regains",
                  "Tack&Int","Ball Recoveries","Aerial Win%",
                  "Errors","Pressures","Counterpressures",
                  "Counterpress Regains","Turnovers","Dispossessed"]
}

# ---------------- PAGE TITLE + DESCRIPTION ----------------
st.title("🏆 National League South Dashboard 25/26")
st.write(
    "A visual dashboard for **team performance vs league average** and **player percentile profiles** "
    "using StatsBomb-style metrics."
)

# ---------------- TABS (CLICK HEADINGS) ----------------
tab1, tab2 = st.tabs(["📊 Team Dashboard", "👤 Player Dashboard"])


# =============================================================================
# TEAM DASHBOARD TAB
# =============================================================================
with tab1:
    st.sidebar.header("Team Dashboard Settings")
    selected_team = st.sidebar.selectbox("Choose a Team", team_names)

    def make_team_plot(selected_team):
        team_row = team_df[team_df["Team Name"] == selected_team].iloc[0]

        team_values = team_row[team_metrics].values.astype(float)
        league_values = league_row[team_metrics].values.astype(float)

        colors = ["#2ecc71" if t >= l else "#e00614"
                  for t, l in zip(team_values, league_values)]

        fig, ax = plt.subplots(figsize=(13, 7))
        fig.patch.set_facecolor("#0b0b0b")
        ax.set_facecolor("#0b0b0b")

        y = np.arange(len(team_metrics))
        ax.barh(y, team_values, height=0.52, color=colors, edgecolor="white", linewidth=1)

        # League average markers
        for i, avg in enumerate(league_values):
            ax.plot(avg, i, marker="D", markersize=7, color="#FFFF00", zorder=3)

        # Value labels
        for i, val in enumerate(team_values):
            ax.text(val + max(team_values) * 0.015, i, f"{val:.1f}",
                    va="center", ha="left", color="white", fontsize=10)

        ax.set_yticks(y)
        ax.set_yticklabels(team_metrics, color="white", fontsize=11)
        ax.invert_yaxis()
        ax.tick_params(axis="x", colors="gray")
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", linestyle="--", alpha=0.15)

        for spine in ax.spines.values():
            spine.set_visible(False)

        # Titles
        ax.text(-0.15, 1.20, f"{selected_team.upper()} | TEAM ANALYSIS",
                transform=ax.transAxes, color="white", fontsize=24, fontweight="bold")

        ax.text(-0.15, 1.12,
                "Percentile Rank National League South | Season 2025–26\n"
                "Data: Statsbomb | Graphic: @Neil_barretto",
                transform=ax.transAxes, color="white", fontsize=11)

        # Legend
        ax.text(0.15, 1.05, "■ Above League Avg", transform=ax.transAxes, color="#2ecc71", fontsize=10)
        ax.text(0.35, 1.05, "■ Below League Avg", transform=ax.transAxes, color="#e00614", fontsize=10)
        ax.text(0.60, 1.05, "♦ League Average", transform=ax.transAxes, color="#FFFF00", fontsize=10)

        return fig

    fig = make_team_plot(selected_team)
    st.pyplot(fig)

    if st.button("💾 Save Team PNG"):
        filename = f"{selected_team.replace(' ', '_')}_Team_Performance.png"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        st.success(f"Saved: {save_path}")


# =============================================================================
# PLAYER DASHBOARD TAB
# =============================================================================
with tab2:
    st.sidebar.header("Player Dashboard Settings")

    # --- TEAM DROPDOWN ---
    player_teams = sorted(player_df["Team"].dropna().unique())
    selected_player_team = st.sidebar.selectbox("Choose Team", player_teams)

    # --- PLAYER DROPDOWN FILTERED BY TEAM ---
    filtered_players = player_df[player_df["Team"] == selected_player_team]["Name"].dropna().unique()
    filtered_players = sorted(filtered_players)

    selected_player = st.sidebar.selectbox("Choose Player", filtered_players)

    # --- ROLE DROPDOWN ---
    selected_role = st.sidebar.selectbox("Role", ["Auto", "Attacking", "Midfield", "Defensive"])

    def draw_player_dashboard(player, role_choice):
        row90 = player_df[player_df["Name"] == player].iloc[0]
        rowpct = player_pct_df[player_pct_df["Name"] == player].iloc[0]

        # AUTO ROLE DETECTION (PRIMARY + SECONDARY)
        auto_role = detect_role(row90["Primary Position"], row90["Secondary Position"])
        role = auto_role if role_choice == "Auto" else role_choice

        # Safety: if GK is detected, force Midfield (or you can make GK radar later)
        if role == "Goalkeeper":
            role = "Defensive"

        metrics = radar_metrics[role]
        values = [rowpct[m] for m in metrics]

        # ---------------- FIGURE ----------------
        fig = plt.figure(figsize=(16, 9), facecolor="#ede8d0")
        gs = fig.add_gridspec(2, 3, width_ratios=[1.15, 1.15, 1.6], hspace=0.45, wspace=0.18)

        # -------- GOALS & ASSISTS --------
        ax1 = fig.add_subplot(gs[0, 0:2])
        ax1.set_facecolor("#ede8d0")

        goals, xg = row90["All Goals"], row90["xG"]
        assists, xa = row90["Assists"], row90["xG Assisted"]

        y = np.arange(2)
        h = 0.35

        ax1.barh(y - h/2, [goals, assists], height=h, color="#000000", label="Actual")
        ax1.barh(y + h/2, [xg, xa], height=h, color="#555555", label="Expected")

        ax1.set_yticks(y)
        ax1.set_yticklabels(["Goals", "Assists"], color="black")
        ax1.invert_yaxis()
        ax1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
        ax1.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax1.spines[:].set_visible(False)
        ax1.tick_params(left=False, bottom=False, colors="black")

        # -------- COMPLETION RATES --------
        ax2 = fig.add_subplot(gs[1, 0:2])
        ax2.set_facecolor("#ede8d0")

        comp_labels = ["Shooting%", "Passing%", "Dribble%", "Crossing%", "Carry%"]
        comp_vals = [row90[c] for c in comp_labels]
        y2 = np.arange(len(comp_labels))

        ax2.barh(y2, comp_vals, color="#000000")
        ax2.set_yticks(y2)
        ax2.set_yticklabels(comp_labels, color="black")
        ax2.set_xlim(0, 100)
        ax2.invert_yaxis()
        ax2.set_title("COMPLETION RATE %", color="black", fontweight="bold")
        ax2.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax2.spines[:].set_visible(False)
        ax2.tick_params(left=False, bottom=False, colors="black")

        # -------- PIZZA CHART --------
        ax3 = fig.add_subplot(gs[:, 2], polar=True)
        ax3.set_facecolor("#ede8d0")
        ax3.set_position([0.60, 0.12, 0.38, 0.80])

        baker = PyPizza(
            params=metrics,
            min_range=[0]*len(metrics),
            max_range=[100]*len(metrics),
            background_color="#ede8d0",
            straight_line_color="white",   # dividers
            last_circle_color="black",     # outer circle
            other_circle_lw=1
        )

        baker.make_pizza(
            values,
            ax=ax3,
            figsize=(7, 7),
            kwargs_slices=dict(facecolor="#000000", edgecolor="black", linewidth=1),
            kwargs_params=dict(color="black", fontsize=9),
            kwargs_values=dict(
                color="black",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", fc="#ede8d0", ec="black", lw=0.5)
            )
        )

        ax3.text(
            0.5, -0.08,
            f"{role.upper()} PERCENTILE PROFILE",
            transform=ax3.transAxes,
            ha="center", va="center",
            fontsize=12, fontweight="bold", color="black"
        )

        # -------- TITLE --------
        name = row90["Name"]
        team = row90["Team"]
        nation = row90["Nationality"]
        primary = row90["Primary Position"]
        secondary = row90["Secondary Position"]
        age = int(row90["Age"])

        fig.text(
            0.05, 0.965,
            f"{name.upper()}",
            fontsize=50,
            fontproperties=title_font.prop,
            ha="left", va="center",
            color="black"
        )

        fig.text(
            1, 0.965,
            f"{team} | {nation}\n{primary} | {secondary} | {age}",
            fontsize=18, fontweight="bold",
            ha="right", va="center",
            color="black"
        )

        st.pyplot(fig)

        return fig

    fig_player = draw_player_dashboard(selected_player, selected_role)

    if st.button("💾 Save Player PNG"):
        filename = f"{selected_player.replace(' ', '_')}_Player_Dashboard.png"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        fig_player.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig_player.get_facecolor())
        st.success(f"Saved: {save_path}")
