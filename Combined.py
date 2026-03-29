import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import PyPizza, FontManager
from matplotlib.patches import Patch
import os

# =============================================================================
# STREAMLIT PAGE SETUP
# =============================================================================
st.set_page_config(page_title="National League South Dashboard 25/26", layout="wide")

# =============================================================================
# FILE PATHS
# =============================================================================
TEAM_FILE = "League_Team_Stats (5).csv"
PLAYER_FILE = "National_league_players (Per90).csv"
PLAYER_PCT_FILE = "National_league_players(Percentile).csv"
GK_FILE = "GK (Per90).csv"
GK_PCT_FILE = "GK (Percentile).csv"

OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =============================================================================
# LOAD DATA
# =============================================================================
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

gk_compare_df = pd.read_csv("Search_results_percentiles.csv")
gk_compare_df.columns = gk_compare_df.columns.str.strip()

# =============================================================================
# FONT
# =============================================================================
title_font = FontManager(
    "https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf"
)

# =============================================================================
# THEME
# =============================================================================
BG = "#ede8d0"
TEXT = "black"
GREEN = "#008000"
RED = "#992514"
LEAGUE_MARKER = "#000000"

# =============================================================================
# POSITION → ROLE LOGIC
# =============================================================================
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
        "wing back", "wb", "defensive", "dm", "holding", "back"
    ]
    if any(k in pos_text for k in defensive_keywords):
        return "Defensive"

    attacking_keywords = [
        "forward", "striker", "cf", "st",
        "wing", "rw", "lw", "attacking", "am", "10"
    ]
    if any(k in pos_text for k in attacking_keywords):
        return "Attacking"

    return "Midfield"


# =============================================================================
# TEAM DASHBOARD METRICS
# =============================================================================
team_metrics = [
    "Goals", "NP xG", "Shots", "SP xG", "Corner xG",
    "Passes Inside Box", "Successful Box Cross%", "Dribble%", "Deep Progressions",
    "Possession%", "Passing%", "PPDA", "Aggression", "Counterpressures",
    "Goals Conceded", "NP xG Against", "SP xG Against", "Corner xG Against"
]

league_row = team_df[team_df["Team Name"] == "League Average"].iloc[0]
team_names = sorted(team_df[team_df["Team Name"] != "League Average"]["Team Name"].unique())


# =============================================================================
# PLAYER DASHBOARD METRICS
# =============================================================================
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


# =============================================================================
# GK DASHBOARD METRICS
# =============================================================================
gk_radar_full = [
    "Goals Conceded", "PSxG Faced", "GSAA", "Save%", "xSv%",
    "xG Faced", "Shots Faced", "Shots Faced OT%", "All Shots Faced",
    "Positioning Error", "Penalties Faced", "Penalties Conceded",
    "GK Aggressive Dist.", "Claims%", "Pass into Danger%",
    "Pass into Pressure%", "Positive Outcome", "Positive Outcome%"
]

gk_radar_shotstop = [
    "Goals Conceded", "PSxG Faced", "GSAA", "Save%", "xSv%",
    "xG Faced", "Shots Faced", "Shots Faced OT%", "All Shots Faced", "Positioning Error"
]

gk_radar_distribution = [
    "Passing%", "Pass Length", "Claims%", "GK Aggressive Dist.",
    "Pass into Danger%", "Pass into Pressure%", "Positive Outcome",
    "Positive Outcome%", "Penalties Faced", "Penalties Conceded"
]


# =============================================================================
# PAGE TITLE + DESCRIPTION
# =============================================================================
st.title("🏆 National League South Dashboard 25/26")

st.write("""
This dashboard provides team-level percentile comparisons vs league average and individual player percentile profiles across key performance metrics, using official StatsBomb-style event data for the 2025/26 National League South season.

**How to use:**
- Select **Team Dashboard**, **Player Dashboard**, **Goalkeeper Dashboard** or **GK Comparison** using the tabs above.
- Use the dropdown menus to choose a team and player.
- Team charts compare percentile ranks vs league average.
- Player profiles show percentile performance by role.
""")


# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Team Dashboard",
    "👤 Player Dashboard",
    "🧤 Goalkeeper Dashboard",
    "🆚 GK Comparison"
])


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
        ax.barh(y, team_values, height=0.52, color=colors, edgecolor="black", linewidth=0.8)

        for i, avg in enumerate(league_values):
            ax.plot(avg, i, marker="D", markersize=7, color=LEAGUE_MARKER, zorder=3)

        for i, val in enumerate(team_values):
            ax.text(val + max(team_values) * 0.015, i, f"{val:.1f}",
                    va="center", ha="left", color=TEXT, fontsize=10)

        ax.set_yticks(y)
        ax.set_yticklabels(team_metrics, color=TEXT, fontsize=11)
        ax.invert_yaxis()
        ax.tick_params(axis="x", colors=TEXT)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", linestyle="--", alpha=0.25, color="black")

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.text(-0.15, 1.20, f"{selected_team.upper()} | TEAM ANALYSIS",
                transform=ax.transAxes, color=TEXT, fontsize=24, fontweight="bold")
        ax.text(-0.15, 1.12,
                "Percentile Rank National League South | Season 2025–26\nData: Statsbomb | Graphic: @Neil_barretto",
                transform=ax.transAxes, color=TEXT, fontsize=11)
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

        ax2 = fig.add_subplot(gs[1, 0:2])
        ax2.set_facecolor(BG)

        comp_labels = ["Shooting%", "Passing%", "Dribble%", "Crossing%", "Carry%"]
        comp_vals = [row90[c] for c in comp_labels]
        y2 = np.arange(len(comp_labels))

        bars = ax2.barh(y2, comp_vals, color="black")
        for i, b in enumerate(bars):
            val = comp_vals[i]
            ax2.text(val + 1.5, b.get_y() + b.get_height()/2, f"{val:.1f}%",
                     va="center", ha="left", fontsize=10, color=TEXT)

        ax2.set_yticks(y2)
        ax2.set_yticklabels(comp_labels, color=TEXT)
        ax2.set_xlim(0, 100)
        ax2.invert_yaxis()
        ax2.set_title("COMPLETION RATE %", color=TEXT, fontweight="bold")
        ax2.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax2.spines[:].set_visible(False)
        ax2.tick_params(left=False, bottom=False, colors=TEXT)

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
            values, ax=ax3, figsize=(7, 7),
            kwargs_slices=dict(facecolor="black", edgecolor="black", linewidth=1),
            kwargs_params=dict(color=TEXT, fontsize=9),
            kwargs_values=dict(color=TEXT, fontsize=9,
                               bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="black", lw=0.5))
        )

        ax3.text(0.5, -0.08, f"{role.upper()} PERCENTILE PROFILE",
                 transform=ax3.transAxes, ha="center", va="center",
                 fontsize=12, fontweight="bold", color=TEXT)

        name = row90["Name"]
        team = row90["Team"]
        nation = row90["Nationality"]
        primary = row90["Primary Position"]
        secondary = row90["Secondary Position"]
        age = int(row90["Age"])

        fig.text(0.05, 0.965, f"{name.upper()}", fontsize=50,
                 fontproperties=title_font.prop, ha="left", va="center", color=TEXT)
        fig.text(1, 0.965, f"{team} | {nation}\n{primary} | {secondary} | {age}",
                 fontsize=18, fontweight="bold", ha="right", va="center", color=TEXT)

        st.pyplot(fig)
        return fig

    fig_player = draw_player_dashboard(selected_player, selected_role)

    if st.button("💾 Save Player PNG"):
        filename = f"{selected_player.replace(' ', '_')}_Player_Dashboard.png"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        fig_player.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig_player.get_facecolor())
        st.success(f"Saved: {save_path}")


# =============================================================================
# GOALKEEPER DASHBOARD TAB
# =============================================================================
with tab3:
    st.sidebar.header("Goalkeeper Dashboard Settings")

    gk_teams = sorted(gk_df["Team"].dropna().unique())
    selected_gk_team = st.sidebar.selectbox("Choose GK Team", gk_teams)

    gk_players = gk_df[gk_df["Team"] == selected_gk_team]["Name"].dropna().unique()
    gk_players = sorted(gk_players)

    selected_gk = st.sidebar.selectbox("Choose Goalkeeper", gk_players)
    radar_type = st.sidebar.selectbox("Radar Style", ["Full GK Radar", "Split GK Radar (2 charts)"])

    def safe_height(x):
        if pd.isna(x):
            return ""
        return str(x).strip()

    def draw_pizza(ax, metrics, values, subtitle):
        baker = PyPizza(
            params=metrics,
            min_range=[0] * len(metrics),
            max_range=[100] * len(metrics),
            background_color=BG,
            straight_line_color="white",
            last_circle_color="black",
            other_circle_lw=1,
            inner_circle_size=12
        )

        baker.make_pizza(
            values, ax=ax, figsize=(7, 7),
            kwargs_slices=dict(facecolor="black", edgecolor="black", linewidth=1),
            kwargs_params=dict(color=TEXT, fontsize=8),
            kwargs_values=dict(color=TEXT, fontsize=8,
                               bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="black", lw=0.5))
        )

        ax.text(0.5, -0.10, subtitle, transform=ax.transAxes,
                ha="center", va="center", fontsize=12, fontweight="bold", color=TEXT)

    def draw_gk_dashboard(gk_name, radar_choice):
        gk_row = gk_df[gk_df["Name"] == gk_name].iloc[0]
        gk_pct_row = gk_pct_df[gk_pct_df["Name"] == gk_name].iloc[0]

        name = gk_row["Name"]
        team = gk_row["Team"]
        nation = gk_row["Nationality"]
        height = safe_height(gk_row["Height"]) if "Height" in gk_row.index else ""

        fig = plt.figure(figsize=(16, 9), facecolor=BG)

        if radar_choice == "Full GK Radar":
            gs = fig.add_gridspec(2, 3, width_ratios=[1.15, 1.15, 1.6], hspace=0.45, wspace=0.18)
        else:
            gs = fig.add_gridspec(2, 4, width_ratios=[1.1, 1.1, 1.3, 1.3], hspace=0.45, wspace=0.25)

        ax1 = fig.add_subplot(gs[0, 0:2])
        ax1.set_facecolor(BG)

        shot_metrics = ["Save%", "xSv%"]
        shot_vals = [float(gk_row[m]) for m in shot_metrics]
        y = np.arange(len(shot_metrics))

        bars = ax1.barh(y, shot_vals, color="black")
        for i, b in enumerate(bars):
            v = shot_vals[i]
            ax1.text(v + 1.5, b.get_y() + b.get_height() / 2, f"{v:.1f}%",
                     va="center", ha="left", fontsize=12, color=TEXT)

        ax1.set_yticks(y)
        ax1.set_yticklabels(shot_metrics, color=TEXT, fontsize=12)
        ax1.set_xlim(0, 100)
        ax1.invert_yaxis()
        ax1.set_title("SHOT STOPPING %", color=TEXT, fontweight="bold")
        ax1.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax1.spines[:].set_visible(False)
        ax1.tick_params(left=False, bottom=False, colors=TEXT)

        ax2 = fig.add_subplot(gs[1, 0:2])
        ax2.set_facecolor(BG)

        dist_metrics = ["Passing%", "Pass Length", "Pass into Danger%", "Pass into Pressure%"]
        dist_vals = [float(gk_row[m]) for m in dist_metrics]
        y2 = np.arange(len(dist_metrics))

        bars2 = ax2.barh(y2, dist_vals, color="black")
        for i, b in enumerate(bars2):
            v = dist_vals[i]
            ax2.text(v + (1.5 if v <= 95 else -3), b.get_y() + b.get_height() / 2,
                     f"{v:.1f}", va="center", ha="left" if v <= 95 else "right",
                     fontsize=12, color=TEXT)

        ax2.set_yticks(y2)
        ax2.set_yticklabels(dist_metrics, color=TEXT, fontsize=12)
        ax2.invert_yaxis()
        ax2.set_title("DISTRIBUTION & RISK", color=TEXT, fontweight="bold")
        ax2.grid(axis="x", linestyle="--", alpha=0.3, color="black")
        ax2.spines[:].set_visible(False)
        ax2.tick_params(left=False, bottom=False, colors=TEXT)

        if radar_choice == "Full GK Radar":
            metrics = gk_radar_full
            values = [float(gk_pct_row[m]) for m in metrics]
            ax3 = fig.add_subplot(gs[:, 2], polar=True)
            ax3.set_facecolor(BG)
            ax3.set_position([0.60, 0.12, 0.38, 0.80])
            draw_pizza(ax3, metrics, values, "GOALKEEPER PERCENTILE PROFILE")
        else:
            metrics1 = gk_radar_shotstop
            values1 = [float(gk_pct_row[m]) for m in metrics1]
            ax3 = fig.add_subplot(gs[:, 2], polar=True)
            ax3.set_facecolor(BG)
            draw_pizza(ax3, metrics1, values1, "SHOT STOPPING PROFILE")

            metrics2 = gk_radar_distribution
            values2 = [float(gk_pct_row[m]) for m in metrics2]
            ax4 = fig.add_subplot(gs[:, 3], polar=True)
            ax4.set_facecolor(BG)
            draw_pizza(ax4, metrics2, values2, "DISTRIBUTION / CONTROL PROFILE")

        fig.text(0.05, 0.965, f"{name.upper()}", fontsize=50,
                 fontproperties=title_font.prop, ha="left", va="center", color=TEXT)

        right_text = f"{team} | {nation}"
        right_text += f"\nHeight: {height}" if height != "" else "\n"

        fig.text(1, 0.965, right_text, fontsize=18, fontweight="bold",
                 ha="right", va="center", color=TEXT)

        st.pyplot(fig)
        return fig

    fig_gk = draw_gk_dashboard(selected_gk, radar_type)

    if st.button("💾 Save GK PNG"):
        filename = f"{selected_gk.replace(' ', '_')}_GK_Dashboard.png"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        fig_gk.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=fig_gk.get_facecolor())
        st.success(f"Saved: {save_path}")


# =============================================================================
# GK COMPARISON TAB
# =============================================================================
with tab4:
    st.sidebar.header("GK Comparison Settings")

    st.subheader("🆚 Goalkeeper Comparison")
    st.write("Compare two goalkeepers head-to-head using a percentile pizza chart.")

    all_gk_names = sorted(gk_compare_df["Player"].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        gk1 = st.selectbox("Select Goalkeeper 1", all_gk_names, key="gk_comp_1")
        gk1_color = st.color_picker("GK 1 Colour", "#ff0000", key="gk1_color")
    with col2:
        gk2 = st.selectbox("Select Goalkeeper 2", all_gk_names,
                            index=1 if len(all_gk_names) > 1 else 0, key="gk_comp_2")
        gk2_color = st.color_picker("GK 2 Colour", "#00008B", key="gk2_color")

    comp_metric_options = [col for col in gk_compare_df.columns if col != "Player"]

    default_metrics = [
        "Minutes played", "Save rate, %", "Clean sheets",
        "Conceded goals per 90", "Shots against per 90",
        "xG against per 90", "Prevented goals per 90",
        "Exits per 90", "Aerial duels per 90"
    ]
    safe_defaults = [m for m in default_metrics if m in comp_metric_options]

    selected_comp_metrics = st.multiselect(
        "Select metrics to compare (min 3):",
        options=comp_metric_options,
        default=safe_defaults
    )

    def draw_gk_comparison(gk1_name, gk2_name, metrics, color1, color2):
        row1 = gk_compare_df.set_index("Player").loc[gk1_name]
        row2 = gk_compare_df.set_index("Player").loc[gk2_name]

        values1 = [int(float(row1[m])) for m in metrics]
        values2 = [int(float(row2[m])) for m in metrics]

        baker = PyPizza(
            params=metrics,
            min_range=[0] * len(metrics),
            max_range=[100] * len(metrics),
            background_color=BG,
            straight_line_color="#000000",
            last_circle_color="#222222",
            last_circle_lw=2.5,
            other_circle_lw=0,
            other_circle_color="#222222",
            straight_line_lw=1
        )

        fig, ax = baker.make_pizza(
            values1,
            compare_values=values2,
            figsize=(6, 6),
            color_blank_space=[BG] * len(metrics),
            blank_alpha=0.8,
            param_location=110,
            kwargs_slices=dict(facecolor=color1, edgecolor="#000000", zorder=1, linewidth=1),
            kwargs_compare=dict(facecolor=color2, edgecolor="#222222", zorder=3, linewidth=1),
            kwargs_params=dict(color="#222222", fontsize=8, zorder=5, va="center"),
            kwargs_values=dict(
                color="#000000", fontsize=8, zorder=3,
                bbox=dict(edgecolor="#000000", facecolor="#ffffff",
                          boxstyle="round,pad=0.2", lw=1)
            ),
            kwargs_compare_values=dict(
                color="#000000", fontsize=8, zorder=3,
                bbox=dict(edgecolor="#000000", facecolor="#ffffff",
                          boxstyle="round,pad=0.2", lw=1)
            )
        )

        fig.text(0.08, 0.97, f"{gk1_name.upper()} vs {gk2_name.upper()}",
                 fontsize=18, fontweight="bold", color="#222222", ha="left")

        fig.text(0.08, 0.93,
                 "Percentile Rank | National League South | Season 2025–26\n"
                 "Data: @Statsbomb | Graphic: @Neil_barretto",
                 fontsize=9, color="#222222", ha="left")

        legend_elements = [
            Patch(facecolor=color1, edgecolor="#000000", label=gk1_name),
            Patch(facecolor=color2, edgecolor="#000000", label=gk2_name)
        ]
        fig.legend(handles=legend_elements, loc="upper right",
                   bbox_to_anchor=(0.92, 0.97), frameon=False, fontsize=9)

        return fig

    if len(selected_comp_metrics) < 3:
        st.warning("Please select at least 3 metrics.")
    elif gk1 == gk2:
        st.warning("Please select two different goalkeepers.")
    else:
        fig_comp = draw_gk_comparison(gk1, gk2, selected_comp_metrics, gk1_color, gk2_color)
        st.pyplot(fig_comp)

        if st.button("💾 Save Comparison PNG"):
            filename = f"{gk1.replace(' ', '_')}_vs_{gk2.replace(' ', '_')}_GK_Comparison.png"
            save_path = os.path.join(OUTPUT_FOLDER, filename)
            fig_comp.savefig(save_path, dpi=300, bbox_inches="tight",
                             facecolor=fig_comp.get_facecolor())
            st.success(f"Saved: {save_path}")
