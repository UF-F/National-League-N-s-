import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Patch
import streamlit as st
from statsbombpy import sb
from mplsoccer import VerticalPitch, Pitch, Radar, FontManager
 
# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Dagenham & Redbridge | Coaching Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# =============================================================================
# THEME
# =============================================================================
BG        = "#ede8d0"
TEXT      = "#1a1a1a"
RED       = "#c0392b"
DARK_RED  = "#7b1e13"
CREAM     = "#ede8d0"
MID       = "#c8c3a8"
SUBTLE    = "#9a9580"
WHITE     = "#ffffff"
 
# =============================================================================
# GLOBAL STYLES
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;500;600&family=Barlow+Condensed:wght@400;600;700&display=swap');
 
html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #ede8d0;
    color: #1a1a1a;
}
 
.stApp { background-color: #ede8d0; }
 
/* Header */
.dash-header {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 3px solid #c0392b;
    margin-bottom: 1.5rem;
}
.dash-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    color: #c0392b;
    letter-spacing: 2px;
    line-height: 1;
    margin: 0;
}
.dash-subtitle {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    color: #9a9580;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0;
}
 
/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #d8d3ba;
    border-radius: 4px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #9a9580;
    background-color: transparent;
    border-radius: 3px;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background-color: #c0392b !important;
    color: #ede8d0 !important;
}
 
/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1a1a1a;
}
[data-testid="stSidebar"] * {
    color: #ede8d0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ede8d0 !important;
    font-family: 'Barlow Condensed', sans-serif;
}
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #2a2a2a !important;
    color: #ede8d0 !important;
}
 
/* Metric cards */
.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.metric-card {
    background: #d8d3ba;
    border-left: 4px solid #c0392b;
    border-radius: 4px;
    padding: 12px 20px;
    flex: 1;
    min-width: 130px;
}
.metric-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #9a9580;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: #c0392b;
    line-height: 1;
}
.metric-sub {
    font-size: 0.75rem;
    color: #9a9580;
    margin-top: 2px;
}
 
/* Section headers */
.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    color: #1a1a1a;
    letter-spacing: 2px;
    border-bottom: 2px solid #c0392b;
    padding-bottom: 4px;
    margin-bottom: 1rem;
}
 
/* Info box */
.info-box {
    background: #d8d3ba;
    border-radius: 4px;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #9a9580;
    margin-bottom: 1rem;
}
 
/* Spinner override */
.stSpinner > div { border-top-color: #c0392b !important; }
 
/* Selectbox */
.stSelectbox [data-baseweb="select"] {
    background-color: #d8d3ba;
    border-color: #c8c3a8;
}
 
/* Buttons */
.stButton > button {
    background-color: #c0392b;
    color: #ede8d0;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    border: none;
    border-radius: 3px;
    padding: 8px 24px;
}
.stButton > button:hover {
    background-color: #7b1e13;
}
</style>
""", unsafe_allow_html=True)
 
# =============================================================================
# CREDENTIALS
# =============================================================================
creds = {
    "user":   st.secrets["SB_USERNAME"],
    "passwd": st.secrets["SB_PASSWORD"]
}
 
COMPETITION_ID = 64
SEASON_ID      = 318
TEAM_NAME      = "Dagenham & Redbridge"
 
# =============================================================================
# DATA LOADING — cached
# =============================================================================
@st.cache_data(show_spinner=False)
def load_matches():
    matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID, creds=creds)
    team_matches = matches[
        (matches["home_team"] == TEAM_NAME) |
        (matches["away_team"] == TEAM_NAME)
    ].copy()
    return team_matches
 
@st.cache_data(show_spinner=False)
def load_all_team_events(_team_matches):
    all_events = []
    for mid in _team_matches["match_id"].tolist():
        try:
            events = sb.events(match_id=mid, creds=creds)
            if isinstance(events, pd.DataFrame) and len(events) > 0:
                all_events.append(events)
        except Exception:
            continue
    if all_events:
        return pd.concat(all_events, ignore_index=True)
    return pd.DataFrame()
 
@st.cache_data(show_spinner=False)
def load_player_events(_team_matches, player_name):
    all_events = []
    for mid in _team_matches["match_id"].tolist():
        try:
            events = sb.events(match_id=mid, creds=creds)
            if isinstance(events, pd.DataFrame) and len(events) > 0:
                player_ev = events[events["player"] == player_name]
                if len(player_ev) > 0:
                    all_events.append(player_ev)
        except Exception:
            continue
    if all_events:
        return pd.concat(all_events, ignore_index=True)
    return pd.DataFrame()
 
# =============================================================================
# MATPLOTLIB HELPERS
# =============================================================================
def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=SUBTLE)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MID)
    ax.yaxis.label.set_color(SUBTLE)
    ax.xaxis.label.set_color(SUBTLE)
 
def style_fig(fig):
    fig.patch.set_facecolor(BG)
 
def fig_title(fig, title, subtitle=""):
    fig.text(0.5, 0.98, title,
             ha="center", fontsize=15, fontweight="bold",
             color=TEXT, fontfamily="sans-serif")
    if subtitle:
        fig.text(0.5, 0.95, subtitle,
                 ha="center", fontsize=9, color=SUBTLE)
 
# =============================================================================
# SEASON STATS COMPUTATION
# =============================================================================
@st.cache_data(show_spinner=False)
def compute_season_stats(_df, _team_matches):
    dag     = _df[_df["team"] == TEAM_NAME].copy()
    records = []
 
    for mid in dag["match_id"].unique():
        match_df   = dag[dag["match_id"] == mid]
        opp_df     = _df[(_df["match_id"] == mid) & (_df["team"] != TEAM_NAME)]
        match_info = _team_matches[_team_matches["match_id"] == mid]
        if len(match_info) == 0:
            continue
        match_info = match_info.iloc[0]
 
        shots     = match_df[match_df["type"] == "Shot"]
        opp_shots = opp_df[opp_df["type"] == "Shot"]
 
        goals_scored  = len(shots[shots["shot_outcome"] == "Goal"])
        goals_conceded = len(opp_shots[opp_shots["shot_outcome"] == "Goal"])
        xg_for        = shots["shot_statsbomb_xg"].sum()
        xg_against    = opp_shots["shot_statsbomb_xg"].sum()
        shots_on      = len(shots[shots["shot_outcome"].isin(["Saved", "Goal"])])
        opp_shots_on  = len(opp_shots[opp_shots["shot_outcome"].isin(["Saved", "Goal"])])
        passes        = match_df[match_df["type"] == "Pass"]
        pass_comp     = passes[passes["pass_outcome"].isna()]
        pass_pct      = len(pass_comp) / len(passes) * 100 if len(passes) > 0 else 0
        pressures     = len(match_df[match_df["type"] == "Pressure"])
        clearances    = len(match_df[match_df["type"] == "Clearance"])
        interceptions = len(match_df[match_df["type"] == "Interception"])
        is_home       = match_info["home_team"] == TEAM_NAME
        opponent      = match_info["away_team"] if is_home else match_info["home_team"]
 
        records.append({
            "match_id":       mid,
            "date":           pd.to_datetime(match_info["match_date"]),
            "opponent":       opponent,
            "home":           is_home,
            "goals_scored":   goals_scored,
            "goals_conceded": goals_conceded,
            "result":         "W" if goals_scored > goals_conceded else ("D" if goals_scored == goals_conceded else "L"),
            "xg_for":         round(xg_for, 2),
            "xg_against":     round(xg_against, 2),
            "shots":          len(shots),
            "shots_on_tgt":   shots_on,
            "opp_shots_on":   opp_shots_on,
            "pass_pct":       round(pass_pct, 1),
            "pressures":      pressures,
            "clearances":     clearances,
            "interceptions":  interceptions,
        })
 
    stats = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    stats["match_num"] = range(1, len(stats) + 1)
    for col in ["xg_for", "xg_against", "shots", "shots_on_tgt", "pressures", "pass_pct"]:
        stats[f"{col}_roll"] = stats[col].rolling(5, min_periods=1).mean()
    return stats
 
# =============================================================================
# MINUTES PLAYED
# =============================================================================
@st.cache_data(show_spinner=False)
def compute_minutes(_df, _team_matches):
    dag           = _df[_df["team"] == TEAM_NAME].copy()
    player_minutes = {}
 
    for mid in _team_matches["match_id"].tolist():
        match_df = dag[dag["match_id"] == mid]
        starters = match_df[match_df["type"] == "Starting XI"]
        if len(starters) == 0:
            continue
 
        tactics = starters.iloc[0].get("tactics", {})
        lineup  = tactics.get("lineup", []) if isinstance(tactics, dict) else []
 
        match_players = {}
        for item in lineup:
            p = item.get("player", {})
            name = p.get("name") if isinstance(p, dict) else None
            if name:
                match_players[name] = {"on": 0, "off": 90}
 
        for _, sub in match_df[match_df["type"] == "Substitution"].iterrows():
            sub_name = sub["player"]
            sub_min  = sub["minute"]
            replacement = sub.get("substitution_replacement")
            if isinstance(replacement, dict):
                replacement = replacement.get("name")
            if sub_name in match_players:
                match_players[sub_name]["off"] = sub_min
            if replacement:
                match_players[replacement] = {"on": sub_min, "off": 90}
 
        for player, times in match_players.items():
            mins = times["off"] - times["on"]
            player_minutes[player] = player_minutes.get(player, 0) + mins
 
    return pd.DataFrame([
        {"player": p, "minutes": m}
        for p, m in player_minutes.items()
    ]).sort_values("minutes", ascending=False).reset_index(drop=True)
 
# =============================================================================
# HEADER
# =============================================================================
col_logo, col_title = st.columns([1, 8])
with col_logo:
    try:
        st.image("Dagenham_and_Redbridge_FC_crest.svg.png", width=80)
    except Exception:
        pass
with col_title:
    st.markdown("""
    <div>
        <div class="dash-title">Dagenham & Redbridge FC</div>
        <div class="dash-subtitle">Coaching Intelligence Dashboard &nbsp;·&nbsp; National League South 2025/26</div>
    </div>
    """, unsafe_allow_html=True)
 
st.markdown("<div style='border-bottom:3px solid #c0392b;margin-bottom:1.5rem'></div>",
            unsafe_allow_html=True)
 
# =============================================================================
# LOAD CORE DATA
# =============================================================================
with st.spinner("Loading season data..."):
    team_matches = load_matches()
 
with st.spinner("Loading match events..."):
    df = load_all_team_events(team_matches)
 
# =============================================================================
# TABS
# =============================================================================
tab1, tab2 = st.tabs(["📊  Team Overview", "👤  Player Dashboard"])
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — TEAM OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    if df.empty:
        st.warning("No event data loaded.")
    else:
        stats_df = compute_season_stats(df, team_matches)
        dag      = df[df["team"] == TEAM_NAME]
 
        # ── Summary metrics ──────────────────────────────────────────────────
        total_matches = len(stats_df)
        wins   = len(stats_df[stats_df["result"] == "W"])
        draws  = len(stats_df[stats_df["result"] == "D"])
        losses = len(stats_df[stats_df["result"] == "L"])
        pts    = wins * 3 + draws
        gf     = stats_df["goals_scored"].sum()
        ga     = stats_df["goals_conceded"].sum()
        xgf    = stats_df["xg_for"].sum()
        xga    = stats_df["xg_against"].sum()
 
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-label">Matches</div>
                <div class="metric-value">{total_matches}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Record</div>
                <div class="metric-value">{wins}W {draws}D {losses}L</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Points</div>
                <div class="metric-value">{pts}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Goals</div>
                <div class="metric-value">{gf} / {ga}</div>
                <div class="metric-sub">For / Against</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total xG</div>
                <div class="metric-value">{xgf:.1f} / {xga:.1f}</div>
                <div class="metric-sub">For / Against</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">xG Diff</div>
                <div class="metric-value" style="color:{'#2ecc71' if xgf-xga>=0 else '#c0392b'}">{xgf-xga:+.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
        # ── Chart selector ───────────────────────────────────────────────────
        st.markdown('<div class="section-header">Season Charts</div>', unsafe_allow_html=True)
 
        chart_choice = st.selectbox("Select chart", [
            "xG For vs xG Against",
            "Shots on Target For vs Against",
            "Defensive Actions",
            "Pass % + Results",
            "Home vs Away Radar",
            "Where They Concede From",
            "Minutes Played per Player",
        ], label_visibility="collapsed")
 
        result_colors = {"W": "#2ecc71", "D": "#9a9580", "L": "#c0392b"}
        x = stats_df["match_num"]
 
        # ── xG For vs Against ────────────────────────────────────────────────
        if chart_choice == "xG For vs xG Against":
            fig, ax = plt.subplots(figsize=(14, 5))
            style_fig(fig); style_ax(ax)
            ax.fill_between(x, stats_df["xg_for_roll"],    alpha=0.25, color=RED)
            ax.fill_between(x, stats_df["xg_against_roll"], alpha=0.25, color=TEXT)
            ax.plot(x, stats_df["xg_for_roll"],    color=RED,  lw=2, label="xG For (5-match avg)")
            ax.plot(x, stats_df["xg_against_roll"], color=TEXT, lw=2, label="xG Against (5-match avg)")
            ax.scatter(x, stats_df["xg_for"],    c=RED,  s=20, zorder=5, alpha=0.5)
            ax.scatter(x, stats_df["xg_against"], c=TEXT, s=20, zorder=5, alpha=0.5)
            ax.axhline(stats_df["xg_for"].mean(),    color=RED,  lw=0.8, ls="--", alpha=0.5)
            ax.axhline(stats_df["xg_against"].mean(), color=TEXT, lw=0.8, ls="--", alpha=0.5)
            ax.text(x.max()+0.3, stats_df["xg_for"].mean(),    f"avg {stats_df['xg_for'].mean():.2f}",    color=RED,  fontsize=7, va="center")
            ax.text(x.max()+0.3, stats_df["xg_against"].mean(), f"avg {stats_df['xg_against'].mean():.2f}", color=TEXT, fontsize=7, va="center")
            for _, row in stats_df.iterrows():
                if row["home"]:
                    ax.axvspan(row["match_num"]-0.5, row["match_num"]+0.5, alpha=0.05, color=RED, zorder=0)
            ax.set_ylabel("xG", color=SUBTLE)
            ax.set_xticks(x)
            ax.set_xticklabels([f"M{r['match_num']}\n{r['opponent'][:8]}" for _, r in stats_df.iterrows()],
                                fontsize=6, color=SUBTLE, rotation=45, ha="right")
            ax.legend(fontsize=8, framealpha=0.3, facecolor=BG, edgecolor=MID, loc="upper left")
            fig_title(fig, "xG For vs xG Against", "5-match rolling average | shaded = home match")
            plt.tight_layout()
            st.pyplot(fig)
 
        # ── Shots on Target ──────────────────────────────────────────────────
        elif chart_choice == "Shots on Target For vs Against":
            fig, ax = plt.subplots(figsize=(14, 5))
            style_fig(fig); style_ax(ax)
            width = 0.4
            ax.bar(x - width/2, stats_df["shots_on_tgt"], width=width, color=RED,  alpha=0.7, label="Shots on Target For")
            ax.bar(x + width/2, stats_df["opp_shots_on"], width=width, color=TEXT, alpha=0.7, label="Shots on Target Against")
            ax.plot(x, stats_df["shots_on_tgt_roll"], color=RED, lw=1.5, ls="--", alpha=0.9)
            for _, row in stats_df.iterrows():
                if row["home"]:
                    ax.axvspan(row["match_num"]-0.5, row["match_num"]+0.5, alpha=0.05, color=RED, zorder=0)
            ax.set_ylabel("Count", color=SUBTLE)
            ax.set_xticks(x)
            ax.set_xticklabels([f"M{r['match_num']}\n{r['opponent'][:8]}" for _, r in stats_df.iterrows()],
                                fontsize=6, color=SUBTLE, rotation=45, ha="right")
            ax.legend(fontsize=8, framealpha=0.3, facecolor=BG, edgecolor=MID, loc="upper left")
            fig_title(fig, "Shots on Target For vs Against", "shaded = home match")
            plt.tight_layout()
            st.pyplot(fig)
 
        # ── Defensive Actions ────────────────────────────────────────────────
        elif chart_choice == "Defensive Actions":
            fig, ax = plt.subplots(figsize=(14, 5))
            style_fig(fig); style_ax(ax)
            ax.plot(x, stats_df["pressures_roll"], color=RED,    lw=2,   label="Pressures (5-match avg)")
            ax.plot(x, stats_df["clearances"],     color=TEXT,   lw=1.5, ls="--", alpha=0.7, label="Clearances")
            ax.plot(x, stats_df["interceptions"],  color=SUBTLE, lw=1.5, ls="--", alpha=0.7, label="Interceptions")
            ax.fill_between(x, stats_df["pressures_roll"], alpha=0.1, color=RED)
            for _, row in stats_df.iterrows():
                if row["home"]:
                    ax.axvspan(row["match_num"]-0.5, row["match_num"]+0.5, alpha=0.05, color=RED, zorder=0)
            ax.set_ylabel("Count", color=SUBTLE)
            ax.set_xticks(x)
            ax.set_xticklabels([f"M{r['match_num']}\n{r['opponent'][:8]}" for _, r in stats_df.iterrows()],
                                fontsize=6, color=SUBTLE, rotation=45, ha="right")
            ax.legend(fontsize=8, framealpha=0.3, facecolor=BG, edgecolor=MID, loc="upper left")
            fig_title(fig, "Defensive Actions per Match", "5-match rolling pressure average | shaded = home match")
            plt.tight_layout()
            st.pyplot(fig)
 
        # ── Pass % + Results ─────────────────────────────────────────────────
        elif chart_choice == "Pass % + Results":
            fig, ax = plt.subplots(figsize=(14, 5))
            style_fig(fig); style_ax(ax)
            ax.plot(x, stats_df["pass_pct_roll"], color=RED, lw=2, label="Pass % (5-match avg)")
            ax.fill_between(x, stats_df["pass_pct_roll"], alpha=0.15, color=RED)
            ax.set_ylim(50, 95)
            ax.set_ylabel("Pass %", color=SUBTLE)
            for _, row in stats_df.iterrows():
                ax.scatter(row["match_num"], 92,
                           c=result_colors[row["result"]], s=70, zorder=5)
                ax.text(row["match_num"], 89,
                        f"{row['goals_scored']}-{row['goals_conceded']}",
                        ha="center", fontsize=6, color=SUBTLE)
                if row["home"]:
                    ax.axvspan(row["match_num"]-0.5, row["match_num"]+0.5, alpha=0.05, color=RED, zorder=0)
            ax.set_xticks(x)
            ax.set_xticklabels([f"M{r['match_num']}\n{r['opponent'][:8]}" for _, r in stats_df.iterrows()],
                                fontsize=6, color=SUBTLE, rotation=45, ha="right")
            w_patch = mpatches.Patch(color="#2ecc71", label="Win")
            d_patch = mpatches.Patch(color="#9a9580", label="Draw")
            l_patch = mpatches.Patch(color="#c0392b", label="Loss")
            ax.legend(handles=[w_patch, d_patch, l_patch],
                      fontsize=8, framealpha=0.3, facecolor=BG, edgecolor=MID, loc="lower left")
            fig_title(fig, "Pass Completion % + Results", "5-match rolling average | shaded = home match")
            plt.tight_layout()
            st.pyplot(fig)
 
        # ── Home vs Away Radar ───────────────────────────────────────────────
        elif chart_choice == "Home vs Away Radar":
            home_df = stats_df[stats_df["home"] == True]
            away_df = stats_df[stats_df["home"] == False]
 
            labels = ["xG For","xG Against","Shots","Shots on\nTarget","Pass %","Pressures","Clearances","Interceptions"]
            home_values = [
                home_df["xg_for"].mean(), home_df["xg_against"].mean(),
                home_df["shots"].mean(),  home_df["shots_on_tgt"].mean(),
                home_df["pass_pct"].mean(), home_df["pressures"].mean(),
                home_df["clearances"].mean(), home_df["interceptions"].mean()
            ]
            away_values = [
                away_df["xg_for"].mean(), away_df["xg_against"].mean(),
                away_df["shots"].mean(),  away_df["shots_on_tgt"].mean(),
                away_df["pass_pct"].mean(), away_df["pressures"].mean(),
                away_df["clearances"].mean(), away_df["interceptions"].mean()
            ]
            low  = [0,   0,   5,  1, 55, 100, 20,  3]
            high = [2.5, 2.5, 18, 7, 75, 200, 45, 12]
 
            radar = Radar(labels, low, high, num_rings=4, ring_width=1, center_circle_radius=1)
            fig, ax = radar.setup_axis(figsize=(8, 8))
            style_fig(fig)
            ax.set_facecolor(BG)
 
            radar.draw_circles(ax=ax, facecolor="#d8d3ba", edgecolor=MID)
            r1 = radar.draw_radar(home_values, ax=ax,
                                   kwargs_radar={"facecolor": RED, "alpha": 0.4},
                                   kwargs_rings={"facecolor": RED, "alpha": 0.1})
            r2 = radar.draw_radar(away_values, ax=ax,
                                   kwargs_radar={"facecolor": TEXT, "alpha": 0.35},
                                   kwargs_rings={"facecolor": TEXT, "alpha": 0.1})
            _, _, hv = r1
            _, _, av = r2
            ax.scatter(hv[:, 0], hv[:, 1], c=RED,  s=40, zorder=5)
            ax.scatter(av[:, 0], av[:, 1], c=TEXT, s=40, zorder=5)
            radar.draw_range_labels(ax=ax, fontsize=8,  color=SUBTLE)
            radar.draw_param_labels(ax=ax, fontsize=10, color=TEXT)
            legend_elements = [
                Patch(facecolor=RED,  alpha=0.6, label=f"Home ({len(home_df)} matches)"),
                Patch(facecolor=TEXT, alpha=0.5, label=f"Away ({len(away_df)} matches)"),
            ]
            ax.legend(handles=legend_elements, loc="lower center",
                      bbox_to_anchor=(0.5, -0.07), fontsize=9,
                      framealpha=0.3, facecolor=BG, edgecolor=MID, ncol=2)
            fig_title(fig, "Home vs Away Performance", "Per match averages")
            plt.tight_layout()
            st.pyplot(fig)
 
        # ── Goals Conceded ───────────────────────────────────────────────────
        elif chart_choice == "Where They Concede From":
            opp_shots = df[
                (df["team"] != TEAM_NAME) &
                (df["type"] == "Shot") &
                (df["match_id"].isin(team_matches["match_id"]))
            ].copy()
            goals_conceded = opp_shots[opp_shots["shot_outcome"] == "Goal"].copy()
 
            if len(goals_conceded) == 0:
                st.info("No goals conceded data found.")
            else:
                goals_conceded["x"] = goals_conceded["location"].apply(lambda l: l[0])
                goals_conceded["y"] = goals_conceded["location"].apply(lambda l: l[1])
                opp_shots["x"]      = opp_shots["location"].apply(lambda l: l[0])
                opp_shots["y"]      = opp_shots["location"].apply(lambda l: l[1])
 
                pitch = VerticalPitch(pitch_type="statsbomb", pitch_color=BG,
                                      line_color=MID, half=True, pad_top=5, goal_type="box")
                fig, axes = plt.subplots(1, 2, figsize=(14, 8))
                style_fig(fig)
 
                # Left — scatter
                pitch.draw(ax=axes[0])
                axes[0].set_facecolor(BG)
                pitch.scatter(opp_shots["x"], opp_shots["y"], ax=axes[0],
                              s=20, c=SUBTLE, alpha=0.2, zorder=2)
                sizes = (goals_conceded["shot_statsbomb_xg"] * 1500).clip(lower=60)
                pitch.scatter(goals_conceded["x"], goals_conceded["y"], ax=axes[0],
                              s=sizes, c=RED, alpha=0.8, zorder=5,
                              edgecolors=TEXT, linewidths=0.5)
                top5 = goals_conceded.nlargest(5, "shot_statsbomb_xg")
                for _, row in top5.iterrows():
                    axes[0].annotate(
                        f"{row['shot_statsbomb_xg']:.2f}\n{row['player'].split()[-1]}",
                        xy=(row["y"], row["x"]),
                        fontsize=6, color=TEXT, ha="center", va="bottom",
                        xytext=(0, 8), textcoords="offset points"
                    )
                axes[0].set_title("Goals Conceded — Location & xG", color=TEXT, fontsize=11, pad=10)
 
                # Right — heatmap
                pitch.draw(ax=axes[1])
                axes[1].set_facecolor(BG)
                bin_stat = pitch.bin_statistic(goals_conceded["x"], goals_conceded["y"],
                                               statistic="count", bins=(8, 5))
                pitch.heatmap(bin_stat, ax=axes[1], cmap="Reds", alpha=0.7)
                pitch.scatter(goals_conceded["x"], goals_conceded["y"], ax=axes[1],
                              s=20, c=TEXT, alpha=0.4, zorder=3)
                axes[1].set_title("Goals Conceded — Density", color=TEXT, fontsize=11, pad=10)
 
                total_xg = goals_conceded["shot_statsbomb_xg"].sum()
                fig_title(fig,
                          "Where Dagenham Concede From",
                          f"{len(goals_conceded)} goals from {len(opp_shots)} opp shots | Total xG conceded: {total_xg:.2f} | Avg xG/goal: {total_xg/len(goals_conceded):.2f}")
                plt.tight_layout()
                st.pyplot(fig)
 
        # ── Minutes Played ───────────────────────────────────────────────────
        elif chart_choice == "Minutes Played per Player":
            minutes_df = compute_minutes(df, team_matches)
            if minutes_df.empty:
                st.info("No minutes data available.")
            else:
                minutes_df = minutes_df.sort_values("minutes", ascending=True)
 
                def get_color(m):
                    if m >= 2000: return RED
                    elif m >= 1000: return "#8b4513"
                    elif m >= 500:  return SUBTLE
                    else:           return MID
 
                colors = [get_color(m) for m in minutes_df["minutes"]]
                max_mins = len(team_matches) * 90
 
                fig, ax = plt.subplots(figsize=(12, max(8, len(minutes_df) * 0.4)))
                style_fig(fig); style_ax(ax)
                ax.spines["left"].set_visible(False)
 
                bars = ax.barh(minutes_df["player"], minutes_df["minutes"],
                               color=colors, edgecolor=BG, linewidth=0.5, height=0.7)
                for bar, mins in zip(bars, minutes_df["minutes"]):
                    ax.text(bar.get_width() + 15,
                            bar.get_y() + bar.get_height() / 2,
                            f"{int(mins)}", va="center", fontsize=8, color=SUBTLE)
 
                ax.axvline(max_mins,    color=RED,   lw=1, ls="--", alpha=0.5)
                ax.axvline(max_mins/2, color=SUBTLE, lw=0.8, ls="--", alpha=0.4)
                ax.text(max_mins + 10,   -0.8, f"Max\n{max_mins}", color=RED,   fontsize=7, va="top")
                ax.text(max_mins/2 + 10, -0.8, "50%",               color=SUBTLE, fontsize=7, va="top")
                ax.set_xlim(0, max_mins + 250)
                ax.tick_params(axis="y", labelsize=9, labelcolor=TEXT)
                ax.tick_params(axis="x", labelsize=8, labelcolor=SUBTLE)
                ax.set_xlabel("Minutes played", color=SUBTLE)
 
                legend_elements = [
                    mpatches.Patch(color=RED,      label="Key player (2000+ mins)"),
                    mpatches.Patch(color="#8b4513", label="Regular (1000-2000 mins)"),
                    mpatches.Patch(color=SUBTLE,   label="Squad (500-1000 mins)"),
                    mpatches.Patch(color=MID,      label="Fringe (<500 mins)"),
                ]
                ax.legend(handles=legend_elements, loc="lower right", fontsize=8,
                          framealpha=0.3, facecolor=BG, edgecolor=MID)
                fig_title(fig, "Minutes Played per Player",
                          f"{len(team_matches)} matches | {len(minutes_df)} players used")
                plt.tight_layout()
                st.pyplot(fig)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — PLAYER DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Player Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select a player to load their individual data. Charts load on demand.</div>',
                unsafe_allow_html=True)
 
    # Sidebar controls for player tab
    with st.sidebar:
        st.markdown("### Player Selection")
        dag_events     = df[df["team"] == TEAM_NAME] if not df.empty else pd.DataFrame()
        dag_players    = sorted(dag_events["player"].dropna().unique().tolist()) if not dag_events.empty else []
        selected_player = st.selectbox("Select Player", dag_players)
 
        st.markdown("### Chart")
        player_chart = st.selectbox("Select View", [
            "Performance Radar",
            "Shot Map",
            "Pass Map",
            "Progressive Carries",
        ])
 
    if not selected_player:
        st.info("Select a player from the sidebar.")
    else:
        with st.spinner(f"Loading {selected_player}'s data..."):
            player_df = load_player_events(team_matches, selected_player)
 
        if player_df.empty:
            st.warning(f"No data found for {selected_player}.")
        else:
            # Player summary metrics
            matches_played = player_df["match_id"].nunique()
            sub_off        = player_df[player_df["type"] == "Substitution"]["minute"]
            total_mins     = (matches_played - len(sub_off)) * 90 + sub_off.sum() if len(sub_off) > 0 else matches_played * 90
            p90            = total_mins / 90 if total_mins > 0 else 1
 
            passes_df  = player_df[player_df["type"] == "Pass"]
            shots_df   = player_df[player_df["type"] == "Shot"]
            goals_df   = shots_df[shots_df["shot_outcome"] == "Goal"]
            carries_df = player_df[player_df["type"] == "Carry"]
            pass_comp  = passes_df[passes_df["pass_outcome"].isna()]
            pass_pct   = len(pass_comp) / len(passes_df) * 100 if len(passes_df) > 0 else 0
 
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-label">Player</div>
                    <div class="metric-value" style="font-size:1.4rem">{selected_player}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Appearances</div>
                    <div class="metric-value">{matches_played}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Minutes</div>
                    <div class="metric-value">{int(total_mins)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Goals</div>
                    <div class="metric-value">{len(goals_df)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Shots p90</div>
                    <div class="metric-value">{len(shots_df)/p90:.1f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Pass %</div>
                    <div class="metric-value">{pass_pct:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
 
            # ── Performance Radar ─────────────────────────────────────────────
            if player_chart == "Performance Radar":
                dribbles_df = player_df[player_df["type"] == "Dribble"]
                drib_comp   = dribbles_df[dribbles_df["dribble_outcome"] == "Complete"]
                pressures_df = player_df[player_df["type"] == "Pressure"]
                ball_rec    = player_df[player_df["type"] == "Ball Recovery"]
                fouls_won   = player_df[player_df["type"] == "Foul Won"]
                shots_on    = shots_df[shots_df["shot_outcome"].isin(["Saved", "Goal"])]
                drib_pct    = len(drib_comp) / len(dribbles_df) * 100 if len(dribbles_df) > 0 else 0
 
                values = [
                    len(shots_df)     / p90,
                    len(shots_on)     / p90,
                    pass_pct,
                    drib_pct,
                    len(pressures_df) / p90,
                    len(ball_rec)     / p90,
                    len(fouls_won)    / p90,
                    len(carries_df)   / p90,
                ]
                labels = [
                    "Shots p90", "Shots on\nTarget p90",
                    "Pass\nCompletion %", "Dribble\nSuccess %",
                    "Pressures p90", "Ball\nRecoveries p90",
                    "Fouls Won p90", "Carries p90",
                ]
                low  = [0,   0,  50,  30,   5,  2,   0,  10]
                high = [5,   3,  90,  90,  30, 12,   5,  50]
 
                radar = Radar(labels, low, high, num_rings=4, ring_width=1, center_circle_radius=1)
                fig, ax = radar.setup_axis(figsize=(8, 8))
                style_fig(fig)
                ax.set_facecolor(BG)
 
                radar.draw_circles(ax=ax, facecolor="#d8d3ba", edgecolor=MID)
                r_out = radar.draw_radar(values, ax=ax,
                                          kwargs_radar={"facecolor": RED, "alpha": 0.5},
                                          kwargs_rings={"facecolor": RED, "alpha": 0.15})
                _, _, verts = r_out
                ax.scatter(verts[:, 0], verts[:, 1], c=RED, s=40, zorder=5)
                radar.draw_range_labels(ax=ax, fontsize=8,  color=SUBTLE)
                radar.draw_param_labels(ax=ax, fontsize=10, color=TEXT)
 
                fig_title(fig, f"{selected_player} — Performance Radar",
                          f"Dagenham & Redbridge | {matches_played} apps | {int(total_mins)} mins")
                plt.tight_layout()
                st.pyplot(fig)
 
            # ── Shot Map ──────────────────────────────────────────────────────
            elif player_chart == "Shot Map":
                if len(shots_df) == 0:
                    st.info("No shots recorded for this player.")
                else:
                    shots = shots_df.copy()
                    shots["x"] = shots["location"].apply(lambda l: l[0])
                    shots["y"] = shots["location"].apply(lambda l: l[1])
                    total_xg   = shots["shot_statsbomb_xg"].sum()
 
                    pitch = VerticalPitch(pitch_type="statsbomb", pitch_color=BG,
                                          line_color=MID, half=True, pad_top=5, goal_type="box")
                    fig, ax = pitch.draw(figsize=(8, 7))
                    style_fig(fig)
                    ax.set_facecolor(BG)
 
                    outcome_styles = {
                        "Goal":    {"color": RED,    "marker": "*", "zorder": 5, "alpha": 1.0},
                        "Saved":   {"color": TEXT,   "marker": "o", "zorder": 4, "alpha": 0.8},
                        "Blocked": {"color": SUBTLE, "marker": "o", "zorder": 4, "alpha": 0.7},
                        "Off T":   {"color": MID,    "marker": "o", "zorder": 3, "alpha": 0.6},
                        "Wayward": {"color": MID,    "marker": "o", "zorder": 3, "alpha": 0.6},
                        "Post":    {"color": "#8b4513", "marker": "o", "zorder": 4, "alpha": 0.9},
                    }
                    for outcome, style in outcome_styles.items():
                        subset = shots[shots["shot_outcome"] == outcome]
                        if len(subset) == 0:
                            continue
                        sizes   = (subset["shot_statsbomb_xg"] * 1500).clip(lower=50)
                        is_goal = style["marker"] == "*"
                        pitch.scatter(subset["x"], subset["y"],
                                      s=sizes * (1.5 if is_goal else 1),
                                      c=style["color"], marker=style["marker"],
                                      ax=ax, zorder=style["zorder"], alpha=style["alpha"],
                                      edgecolors=TEXT, linewidths=0.5,
                                      label=f"{'Goal' if is_goal else outcome} ({len(subset)})")
 
                    ax.legend(loc="lower left", fontsize=8, framealpha=0.3,
                              facecolor=BG, edgecolor=MID)
                    fig_title(fig, f"{selected_player} — Shot Map",
                              f"{len(shots)} shots | {len(goals_df)} goals | xG: {total_xg:.2f} | xG/shot: {total_xg/len(shots):.2f}")
                    plt.tight_layout()
                    st.pyplot(fig)
 
            # ── Pass Map ──────────────────────────────────────────────────────
            elif player_chart == "Pass Map":
                if len(passes_df) == 0:
                    st.info("No passes recorded for this player.")
                else:
                    passes = passes_df.copy()
                    receipts = player_df[player_df["type"] == "Ball Receipt*"].copy()
 
                    passes["x"]     = passes["location"].apply(lambda l: l[0])
                    passes["y"]     = passes["location"].apply(lambda l: l[1])
                    passes["end_x"] = passes["pass_end_location"].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
                    passes["end_y"] = passes["pass_end_location"].apply(lambda l: l[1] if isinstance(l, list) else np.nan)
                    passes["dx"]    = passes["end_x"] - passes["x"]
 
                    completed  = passes[passes["pass_outcome"].isna()].copy()
                    incomplete = passes[passes["pass_outcome"] == "Incomplete"]
                    completed["dx"] = completed["end_x"] - completed["x"]
                    forward  = completed[completed["dx"] >  3]
                    backward = completed[completed["dx"] < -3]
                    lateral  = completed[(completed["dx"] >= -3) & (completed["dx"] <= 3)]
 
                    if len(receipts) > 0:
                        receipts["x"] = receipts["location"].apply(lambda l: l[0])
                        receipts["y"] = receipts["location"].apply(lambda l: l[1])
 
                    pitch = Pitch(pitch_type="statsbomb", pitch_color=BG, line_color=MID)
                    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
                    style_fig(fig)
 
                    for ax_ in axes:
                        pitch.draw(ax=ax_)
                        ax_.set_facecolor(BG)
 
                    for subset, color, alpha, lw, label in [
                        (forward,  RED,    0.5, 2.0, f"Forward ({len(forward)})"),
                        (lateral,  SUBTLE, 0.3, 1.0, f"Lateral ({len(lateral)})"),
                        (backward, "#8b4513", 0.5, 1.5, f"Backward ({len(backward)})"),
                    ]:
                        if len(subset) == 0:
                            continue
                        pitch.arrows(subset["x"], subset["y"],
                                     subset["end_x"], subset["end_y"],
                                     ax=axes[0], color=color, alpha=alpha,
                                     width=lw, headwidth=4, headlength=4, label=label)
 
                    if len(incomplete) > 0:
                        pitch.arrows(incomplete["x"], incomplete["y"],
                                     incomplete["end_x"], incomplete["end_y"],
                                     ax=axes[0], color=TEXT, alpha=0.3,
                                     width=1, headwidth=3, headlength=3,
                                     label=f"Incomplete ({len(incomplete)})")
 
                    axes[0].legend(loc="lower left", fontsize=8, framealpha=0.3,
                                   facecolor=BG, edgecolor=MID)
                    axes[0].set_title("Pass Map", color=TEXT, fontsize=11, pad=8)
 
                    if len(receipts) > 0:
                        bin_stat = pitch.bin_statistic(receipts["x"], receipts["y"],
                                                        statistic="count", bins=(12, 8))
                        pitch.heatmap(bin_stat, ax=axes[1], cmap="Reds", alpha=0.6)
                        pitch.scatter(receipts["x"], receipts["y"], ax=axes[1],
                                      s=15, c=TEXT, alpha=0.3, zorder=3)
                    axes[1].set_title("Receipt Heatmap", color=TEXT, fontsize=11, pad=8)
 
                    comp_pct = len(completed) / len(passes) * 100
                    fig_title(fig, f"{selected_player} — Pass Map",
                              f"{len(passes)} passes | {comp_pct:.1f}% completion | Forward: {len(forward)} | Lateral: {len(lateral)} | Backward: {len(backward)}")
                    plt.tight_layout()
                    st.pyplot(fig)
 
            # ── Progressive Carries ───────────────────────────────────────────
            elif player_chart == "Progressive Carries":
                if len(carries_df) == 0:
                    st.info("No carries recorded for this player.")
                else:
                    carries = carries_df.copy()
                    carries["x"]     = carries["location"].apply(lambda l: l[0])
                    carries["y"]     = carries["location"].apply(lambda l: l[1])
                    carries["end_x"] = carries["carry_end_location"].apply(lambda l: l[0])
                    carries["end_y"] = carries["carry_end_location"].apply(lambda l: l[1])
                    carries["dx"]    = carries["end_x"] - carries["x"]
                    carries["dy"]    = carries["end_y"] - carries["y"]
                    carries["distance"] = np.sqrt(carries["dx"]**2 + carries["dy"]**2)
 
                    progressive = carries[carries["dx"] >= 5]
                    backward    = carries[carries["dx"] <= -3]
                    lateral     = carries[(carries["dx"] > -3) & (carries["dx"] < 5)]
                    prog_short  = progressive[progressive["distance"] <  10]
                    prog_long   = progressive[progressive["distance"] >= 10]
 
                    pitch = Pitch(pitch_type="statsbomb", pitch_color=BG, line_color=MID)
                    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
                    style_fig(fig)
                    for ax_ in axes:
                        pitch.draw(ax=ax_)
                        ax_.set_facecolor(BG)
 
                    for subset, color, alpha, lw, label in [
                        (prog_long,  RED,      0.7, 2.0, f"Progressive >10m ({len(prog_long)})"),
                        (prog_short, "#8b4513", 0.5, 1.5, f"Progressive <10m ({len(prog_short)})"),
                        (lateral,    SUBTLE,   0.25, 1.0, f"Lateral ({len(lateral)})"),
                        (backward,   MID,      0.4, 1.5, f"Backward ({len(backward)})"),
                    ]:
                        if len(subset) == 0:
                            continue
                        pitch.arrows(subset["x"], subset["y"],
                                     subset["end_x"], subset["end_y"],
                                     ax=axes[0], color=color, alpha=alpha,
                                     width=lw, headwidth=4, headlength=4, label=label)
 
                    axes[0].legend(loc="lower left", fontsize=8, framealpha=0.3,
                                   facecolor=BG, edgecolor=MID)
                    axes[0].set_title("Carry Map", color=TEXT, fontsize=11, pad=8)
 
                    if len(progressive) > 0:
                        bin_stat = pitch.bin_statistic(progressive["x"], progressive["y"],
                                                        statistic="count", bins=(12, 8))
                        pitch.heatmap(bin_stat, ax=axes[1], cmap="Reds", alpha=0.65)
                        pitch.scatter(progressive["x"], progressive["y"], ax=axes[1],
                                      s=15, c=TEXT, alpha=0.3, zorder=3)
                    if len(prog_long) > 0:
                        pitch.arrows(prog_long["x"], prog_long["y"],
                                     prog_long["end_x"], prog_long["end_y"],
                                     ax=axes[1], color=RED, alpha=0.6,
                                     width=2, headwidth=5, headlength=5)
                    axes[1].set_title("Progressive Carry Zones", color=TEXT, fontsize=11, pad=8)
 
                    prog_pct  = len(progressive) / len(carries) * 100
                    avg_dist  = carries["distance"].mean()
                    fig_title(fig, f"{selected_player} — Progressive Carries",
                              f"{len(carries)} carries | {prog_pct:.1f}% progressive | Avg distance: {avg_dist:.1f}m | Backward: {len(backward)}")
                    plt.tight_layout()
                    st.pyplot(fig)
