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

GK_FILE = "GK (Per90).csv"
GK_PCT_FILE = "GK (Percentile).csv"

OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------- LOAD DATA ----------------
team_df = pd.read_csv(TEAM_FILE)
team_df.columns = team_df.columns.str.strip()

player_df = pd.read_csv(PLAYER_FILE)
player_df.columns = player_df.columns.str.strip()

player_pct_df = pd.read_csv(PLAYER_PCT_FILE)
player_pct_df.columns = player_pct_df.columns.str.strip()

gk_df = pd.read_csv(GK_FILE)
gk_df.columns = gk_df.columns.str.strip()

gk_pct_df = pd.read_csv(GK_PCT_FILE)
gk_pct_df.columns = gk_pct_df.columns.str.strip()

# ---------------- FONT ----------------
title_font = FontManager(
    "https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf"
)

# ---------------- THEME ----------------
BG = "#ede8d0"
TEXT = "black"

GREEN = "#008000"
RED = "#992514"
LEAGUE_MARKER = "#000000"

# ---------------- POSITION → ROLE LOGIC ----------------
def detect_role(primary_pos, secondary_pos=None):
    positions = []
    if pd.notna(primary_pos):
        positions.append(str(primary_pos))
    if secondary_pos is not None and pd.notna(secondary_pos):
        positions.append(str(secondary_pos))

    pos_text = " | ".join(positions).lower()

    if "keeper" in pos_text or "goal" in pos_text or "gk" in pos_text:
        return "Goalkeeper"

    defensive_keywords = [
        "centre back", "center back", "cb",
        "left back", "right back", "full back",
        "wing back", "wb",
        "defensive", "dm", "holding",
        "back"
    ]
    if any(k in pos_text for k in defensive_keywords):
        return "Defensive"

    attacking_keywords = [
        "forward", "striker", "cf", "st",
        "wing", "rw", "lw",
        "attacking", "am", "10"
    ]
    if any(k in pos_text for k in attacking_keywords):
        return "Attacking"

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

# ---------------- GK DASHBOARD METRICS ----------------
gk_radar_metrics = [
    "Goals Conceded",
    "PSxG Faced",
    "GSAA",
    "Save%",
    "xSv%",
    "Shot Stopping%",
    "xG Faced",
    "Shots Faced",
    "Shots Faced OT%",
    "All Shots Faced",
    "Positioning Error",
    "Penalties Faced",
    "Penalties Conceded",
    "GK Aggressive Dist.",
    "Claims%",
    "Pass into Danger%",
    "Pass into Pressure%",
    "Positive Outcome",
    "Positive Outcome%"
]

# ---------------- PAGE TITLE + DESCRIPTION ----------------
st.title("🏆 National League South Dashboard 25/26")

st.write("""
This dashboard provides team-level percentile comparisons vs league average and individual player percentile profiles across key performance metrics, using official StatsBomb-style event data for the 2025/26 National League South season.

**How to use:**
- Select **Team Dashboard**, **Player Dashboard** or **Goalkeeper Dashboard** using the tabs above.
- Use the dropdown menus to choose a team and player.
- Team charts compare percentile ranks vs league average.
- Player profiles show percentile performance by role.
""")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Team Dashboard", "👤 Player Dashboard", "🧤 Goalkeeper Dashboard"])


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

        colors = [GREEN if t >= l else RED for t, l in zip(team_values, league_values)]

        fig, ax = plt.subplots(figsize=(13, 7))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        y = np.arange(len(team_metrics))
        ax.barh(
            y,
            team_values,
            height=0.52,
            color=colors,
            edgecolor="black",
            linewidth=0.8
        )

        # League average markers
        for i, avg in enumerate(league_values):
            ax.plot(avg, i, marker="D", markersize=7, color=LEAGUE_MARKER, zorder=3)

        # Value labels
        for i, val in enumerate(team_values):
            ax.text(
                val + max(team_values) * 0.015,
                i,
                f"{val:.1f}",
                va="center",
                ha="left",
                color=TEXT,
                fontsize=10
            )

        ax.set_yticks(y)
        ax.set_yticklabels(team_metrics, color=TEXT, fontsize=11)
        ax.invert_yaxis()
        ax.tick_params(axis="x", colors=TEXT)
        ax.tick_params(axis="y", length=0)

        ax.grid(axis="x", linestyle="--", alpha=0.25, color="black")

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.text(
            -0.15,
            1.20,
            f"{selected_team.upper()} | TEAM ANALYSIS",
            transform=ax.transAxes,
            color=TEXT,
            fontsize=24,
            fontweight="bold"
        )

        ax.text(
            -0.15,
            1.12,
            "Percentile Rank National League South | Season 2025–26\n"
            "Data: Statsbomb | Graphic: @Neil_barretto",
            transform=ax.transAxes,
            color=TEXT,
            fontsize=11
        )

        ax.text(0.15, 1.05, "■ Above League Avg", transform=ax.transAxes, color=GREEN, fontsize=10)
        ax.text(0.35, 1.05, "■ Below League Avg", transform=ax.transAxes, color=RED, fontsize=10)
        ax.text(0.60, 1.05, "♦ League Average", transform=ax.transAxes, color=LEAGUE_MARKER, fontsize=10)

        return fig

    fig_team = make_team_plot(selected_team)
    st.pyplot(fig_team)

    if st.button("💾 Save Team PNG"):
        filename = f"{selected_team.replace(' ', '_')}_Team_Performance.png"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        fig_team.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig_team.get_facecolor())
        st.success(f"Saved: {save_path}")


# =============================================================================
# PLAYER DASHBOARD TAB
# =============================================================================
with tab2:
    st.sidebar.header("Player Dashboard Settings")

    player_teams = sorted(player_df["Team"].dropna().unique())
    selected_player_team = st.sidebar.selectbox("Choose Team", player_teams)

    filtered_players = player_df[player_df["Team"] == selected_player_team]["Name"].dropna().unique()
    filtered_players = sorted(filtered_players)

    selected_player = st.sidebar.selectbox("Choose Player", filtered_players)
    selected_role = st.sidebar.selectbox("Role", ["Auto", "Attacking", "Midfield", "Defensive"])

    def draw_player_dashboard(player, role_choice):
        row90 = player_df[player_df["Name"] == player].iloc[0]
        rowpct = player_pct_df[player_pct_df["Name"] == player].iloc[0]

        auto_role = detect_role(row90["Primary Position"], row90["Secondary Position"])
        role = auto_role if role_choice == "Auto" else role_choice

        if role == "Goalkeeper":
            role = "Defensive"

        metrics = radar_metrics[role]
        values = [rowpct[m] for m in metrics]

        fig = plt.figure(figsize=(16, 9), facecolor=BG)
        gs = fig.add_gridspec(2, 3, width_ratios=[1.15, 1.15, 1.6], hspace=0.45, wspace=0.18)

        # -------- GOALS & ASSISTS --------
        ax1 = fig.add_subplot(gs[0, 0:2])
        ax1.set_facecolor(BG)

        goals, xg = row90["All Goals"], row90["xG"]
        assists, xa = row90["Assists"], row90["xG Assisted"]

        y = np.arange(2)
        h = 0.35

        ax1.barh(y - h/2, [goals, assists], height=h, color="black", label="Actual")
        ax1.barh(y + h/2, [xg, xa], height=h, color="#555555", label="Expected")

        ax1.set_yticks(y)
        ax1.set_yticklabels(["Goals", "Assists"], color=TEXT)
        ax1.invert_yaxis()
        ax1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
        ax1.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax1.spines[:].set_visible(False)
        ax1.tick_params(left=False, bottom=False, colors=TEXT)

        # -------- COMPLETION RATES --------
        ax2 = fig.add_subplot(gs[1, 0:2])
        ax2.set_facecolor(BG)

        comp_labels = ["Shooting%", "Passing%", "Dribble%", "Crossing%", "Carry%"]
        comp_vals = [row90[c] for c in comp_labels]
        y2 = np.arange(len(comp_labels))

        bars = ax2.barh(y2, comp_vals, color="black")

        # --- ADD VALUES ON BARS (ONLY HERE) ---
        for i, b in enumerate(bars):
            val = comp_vals[i]
            ax2.text(
                val + 1.5,
                b.get_y() + b.get_height()/2,
                f"{val:.1f}%",
                va="center",
                ha="left",
                fontsize=10,
                color=TEXT
            )

        ax2.set_yticks(y2)
        ax2.set_yticklabels(comp_labels, color=TEXT)
        ax2.set_xlim(0, 100)
        ax2.invert_yaxis()
        ax2.set_title("COMPLETION RATE %", color=TEXT, fontweight="bold")
        ax2.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax2.spines[:].set_visible(False)
        ax2.tick_params(left=False, bottom=False, colors=TEXT)

        # -------- PIZZA CHART --------
        ax3 = fig.add_subplot(gs[:, 2], polar=True)
        ax3.set_facecolor(BG)
        ax3.set_position([0.60, 0.12, 0.38, 0.80])

        baker = PyPizza(
            params=metrics,
            min_range=[0]*len(metrics),
            max_range=[100]*len(metrics),
            background_color=BG,
            straight_line_color="white",
            last_circle_color="black",
            other_circle_lw=1
        )

        baker.make_pizza(
            values,
            ax=ax3,
            figsize=(7, 7),
            kwargs_slices=dict(facecolor="black", edgecolor="black", linewidth=1),
            kwargs_params=dict(color=TEXT, fontsize=9),
            kwargs_values=dict(
                color=TEXT,
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="black", lw=0.5)
            )
        )

        ax3.text(
            0.5,
            -0.08,
            f"{role.upper()} PERCENTILE PROFILE",
            transform=ax3.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=TEXT
        )

        # -------- TITLE --------
        name = row90["Name"]
        team = row90["Team"]
        nation = row90["Nationality"]
        primary = row90["Primary Position"]
        secondary = row90["Secondary Position"]
        age = int(row90["Age"])

        fig.text(
            0.05,
            0.965,
            f"{name.upper()}",
            fontsize=50,
            fontproperties=title_font.prop,
            ha="left",
            va="center",
            color=TEXT
        )

        fig.text(
            1,
            0.965,
            f"{team} | {nation}\n{primary} | {secondary} | {age}",
            fontsize=18,
            fontweight="bold",
            ha="right",
            va="center",
            color=TEXT
        )

        st.pyplot(fig)
        return fig

    fig_player = draw_player_dashboard(selected_player, selected_role)

    if st.button("💾 Save Player PNG"):
        filename = f"{selected_player.replace(' ', '_')}_Player_Dashboard.png"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        fig_player.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig_player.get_facecolor())
        st.success(f"Saved: {save_path}")


# =============================================================================
# GOALKEEPER DASHBOARD TAB (RADAR MODE DROPDOWN + HEIGHT)
# =============================================================================

# =============================================================================
# GOALKEEPER DASHBOARD TAB
# =============================================================================


# =============================================================================
# GOALKEEPER DASHBOARD TAB
# =============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Team Dashboard", "👤 Player Dashboard", "🧤 GK Dashboard"])

with tab3:
    st.sidebar.header("GK Dashboard Settings")

    # ---------------- FILE PATHS ----------------
    GK_FILE = "GK (Per90).csv"
    GK_PCT_FILE = "GK (Percentile).csv"

    # ---------------- LOAD GK DATA ----------------
    gk_df = pd.read_csv(GK_FILE)
    gk_df.columns = gk_df.columns.str.strip()

    gk_pct_df = pd.read_csv(GK_PCT_FILE)
    gk_pct_df.columns = gk_pct_df.columns.str.strip()

    # ---------------- TEAM + PLAYER DROPDOWNS ----------------
    gk_teams = sorted(gk_df["Team"].dropna().unique())
    selected_gk_team = st.sidebar.selectbox("Choose Team", gk_teams)

    filtered_gks = gk_df[gk_df["Team"] == selected_gk_team]["Name"].dropna().unique()
    filtered_gks = sorted(filtered_gks)
    selected_gk = st.sidebar.selectbox("Choose Goalkeeper", filtered_gks)

    # ---------------- RADAR TYPE DROPDOWN ----------------
    radar_type = st.sidebar.selectbox(
        "Radar Type",
        ["Full GK Radar", "Shot Stopping + Sweeping", "Distribution + Decision Making"]
    )

    # ---------------- GK METRICS (PERCENTILES) ----------------
    gk_radar_full = [
        "Goals Conceded", "PSxG Faced", "GSAA", "Save%", "xSv%",
        "xG Faced", "Shots Faced", "Shots Faced OT%", "All Shots Faced",
        "Positioning Error", "Penalties Faced", "Penalties Conceded",
        "GK Aggressive Dist.", "Claims%",
        "Pass into Danger%", "Pass into Pressure%",
        "Positive Outcome", "Positive Outcome%"
    ]

    gk_radar_shotstop = [
        "Goals Conceded", "PSxG Faced", "GSAA", "Save%", "xSv%",
        "Shots Faced", "Shots Faced OT%", "All Shots Faced",
        "GK Aggressive Dist.", "Claims%"
    ]

    gk_radar_distribution = [
        "Passing%", "Pass Length",
        "Pass into Danger%", "Pass into Pressure%",
        "Positive Outcome", "Positive Outcome%"
    ]

    # ---------------- MAIN DRAW FUNCTION ----------------
    def draw_gk_dashboard(gk_name, radar_choice):
        gk_row = gk_df[gk_df["Name"] == gk_name].iloc[0]
        gk_pct_row = gk_pct_df[gk_pct_df["Name"] == gk_name].iloc[0]

        # -------- PICK RADAR METRICS --------
        if radar_choice == "Full GK Radar":
            radar_metrics = gk_radar_full
            radar_title = "GOALKEEPER PERCENTILE PROFILE"
        elif radar_choice == "Shot Stopping + Sweeping":
            radar_metrics = gk_radar_shotstop
            radar_title = "SHOT STOPPING + SWEEPING PROFILE"
        else:
            radar_metrics = gk_radar_distribution
            radar_title = "DISTRIBUTION + DECISION PROFILE"

        radar_values = [float(gk_pct_row[m]) for m in radar_metrics]

        # -------- FIGURE SETUP --------
        fig = plt.figure(figsize=(16, 9), facecolor=BG)
        gs = fig.add_gridspec(2, 3, width_ratios=[1.2, 1.2, 1.6], hspace=0.45, wspace=0.18)

        # =============================================================================
        # SHOT STOPPING % BAR CHART (REMOVE Shot Stopping% metric)
        # =============================================================================
        ax1 = fig.add_subplot(gs[0, 0:2])
        ax1.set_facecolor(BG)

        shot_labels = ["Save%", "xSv%"]  # ✅ Shot Stopping% REMOVED
        shot_vals = [float(gk_row[m]) for m in shot_labels]

        y = np.arange(len(shot_labels))
        ax1.barh(y, shot_vals, color="black")

        # Value labels
        for i, v in enumerate(shot_vals):
            ax1.text(v + 1, i, f"{v:.1f}%", va="center", ha="left", fontsize=12, color=TEXT)

        ax1.set_yticks(y)
        ax1.set_yticklabels(shot_labels, color=TEXT, fontsize=12)
        ax1.set_xlim(0, 100)
        ax1.invert_yaxis()
        ax1.set_title("SHOT STOPPING %", color=TEXT, fontweight="bold")
        ax1.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax1.spines[:].set_visible(False)
        ax1.tick_params(left=False, bottom=False, colors=TEXT)

        # =============================================================================
        # DISTRIBUTION + DECISION MAKING BAR CHART
        # =============================================================================
        ax2 = fig.add_subplot(gs[1, 0:2])
        ax2.set_facecolor(BG)

        dist_labels = ["Passing%", "Pass into Danger%", "Pass into Pressure%", "Positive Outcome%"]
        dist_vals = [float(gk_row[m]) for m in dist_labels]

        y2 = np.arange(len(dist_labels))
        ax2.barh(y2, dist_vals, color="black")

        for i, v in enumerate(dist_vals):
            ax2.text(v + 1, i, f"{v:.1f}%", va="center", ha="left", fontsize=12, color=TEXT)

        ax2.set_yticks(y2)
        ax2.set_yticklabels(dist_labels, color=TEXT, fontsize=12)
        ax2.set_xlim(0, 100)
        ax2.invert_yaxis()
        ax2.set_title("DISTRIBUTION + DECISION MAKING %", color=TEXT, fontweight="bold")
        ax2.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax2.spines[:].set_visible(False)
        ax2.tick_params(left=False, bottom=False, colors=TEXT)

        # =============================================================================
        # PIZZA RADAR (FIXED)
        # =============================================================================
        ax3 = fig.add_subplot(gs[:, 2], projection="polar")
        ax3.set_facecolor(BG)
        ax3.set_position([0.60, 0.12, 0.38, 0.80])

        baker = PyPizza(
            params=radar_metrics,
            min_range=[0] * len(radar_metrics),
            max_range=[100] * len(radar_metrics),
            background_color=BG,
            straight_line_color="white",
            last_circle_color="black",
            other_circle_lw=1,
            inner_circle_size=10  # ✅ prevents the rorigin error
        )

        baker.make_pizza(
            radar_values,
            ax=ax3,
            figsize=(7, 7),
            kwargs_slices=dict(facecolor="black", edgecolor="black", linewidth=1),
            kwargs_params=dict(color=TEXT, fontsize=9),
            kwargs_values=dict(
                color=TEXT,
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="black", lw=0.5)
            )
        )

        ax3.text(
            0.5,
            -0.08,
            radar_title,
            transform=ax3.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=TEXT
        )

        # =============================================================================
        # TITLE + SUBTITLE (HEIGHT INCLUDED)
        # =============================================================================
        name = gk_row["Name"]
        team = gk_row["Team"]
        nation = gk_row["Nationality"]
        age = int(gk_row["Minutes"] * 0 + gk_row["Minutes"] * 0 + gk_row["Minutes"] * 0)  # dummy fallback if needed

        # Height (blank if missing)
        height = ""
        if "Height" in gk_row.index and pd.notna(gk_row["Height"]):
            height = str(gk_row["Height"])

        fig.text(
            0.05,
            0.965,
            f"{name.upper()}",
            fontsize=50,
            fontproperties=title_font.prop,
            ha="left",
            va="center",
            color=TEXT
        )

        subtitle_right = f"{team} | {nation}"
        if height != "":
            subtitle_right += f"\nHeight: {height}"
        else:
            subtitle_right += "\n"

        fig.text(
            1,
            0.965,
            subtitle_right,
            fontsize=18,
            fontweight="bold",
            ha="right",
            va="center",
            color=TEXT
        )

        st.pyplot(fig)
        return fig

    # ---------------- DRAW GK DASHBOARD ----------------
    fig_gk = draw_gk_dashboard(selected_gk, radar_type)

    if st.button("💾 Save GK PNG"):
        filename = f"{selected_gk.replace(' ', '_')}_GK_Dashboard.png"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        fig_gk.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig_gk.get_facecolor())
        st.success(f"Saved: {save_path}")
