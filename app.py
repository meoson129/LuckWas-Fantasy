# filename: app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

st.set_page_config(page_title="Fantasy League Luck Dashboard", layout="wide")

# -------------------------------
# Title & Description
# -------------------------------
st.title("Fantasy League Luck Dashboard")
st.markdown("""
Upload a CSV file containing your league data with the following columns:
- `Team`: Team name
- `PF`: Points For
- `PA`: Points Against

The app will calculate Expected PA, Luck Score, rank teams from Luckiest → Unluckiest,
and display a gradient Luck Score chart.
""")

# -------------------------------
# File uploader
# -------------------------------
uploaded_file = st.file_uploader("Upload your league CSV", type="csv")

if uploaded_file:
    # -------------------------------
    # STEP 1: Load data and compute Expected PA and Luck Score
    # -------------------------------
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in ["Team", "PF", "PA"]):
        st.error("CSV must contain columns: Team, PF, PA")
    else:
        N = len(df)
        df["Expected_PA"] = [(df["PF"].sum() - pf)/(N-1) for pf in df["PF"]]

        # Round numbers
        df["PF"] = df["PF"].round(2)
        df["PA"] = df["PA"].round(2)
        df["Expected_PA"] = df["Expected_PA"].round(2)
        df["Luck_Score"] = (df["Expected_PA"] - df["PA"]).round(2)

        # Sort by Luck Score (Luckiest → Unluckiest)
        df = df.sort_values("Luck_Score", ascending=False).reset_index(drop=True)
        df["Luck_Rank"] = range(1, len(df)+1)

        # Leaderboard
        leaderboard = df[["Luck_Rank", "Team", "PF", "PA", "Expected_PA", "Luck_Score"]]
        leaderboard = leaderboard.rename(columns={
            "PF": "Real PF",
            "PA": "Real PA",
            "Expected_PA": "Expected PA"
        })

        st.subheader("Leaderboard")
        st.dataframe(leaderboard.style.format({
            "Real PF": "{:.2f}",
            "Real PA": "{:.2f}",
            "Expected PA": "{:.2f}",
            "Luck_Score": "{:.2f}"
        }))

        # -------------------------------
        # STEP 2: Plot Luck Score chart
        # -------------------------------
        st.subheader("Luck Score Gradient Chart")

        fig, ax = plt.subplots(figsize=(10, 6))
        norm = plt.Normalize(df["Luck_Score"].min(), df["Luck_Score"].max())
        cmap = plt.cm.RdYlGn
        colors = cmap(norm(df["Luck_Score"]))

        bars = ax.barh(df["Team"], df["Luck_Score"], color=colors, edgecolor='black')

        for bar, score in zip(bars, df["Luck_Score"]):
            width = bar.get_width()
            ax.text(width + (0.02 * df["Luck_Score"].max()), bar.get_y() + bar.get_height()/2,
                    f"{score:.2f}", va='center', fontsize=10)

        ax.invert_yaxis()
        ax.set_xlabel("Luck Score (Expected PA - Actual PA)", fontsize=12)
        ax.set_title("Fantasy League Luck Leaderboard (Luckiest → Unluckiest)", fontsize=14, pad=15)
        ax.grid(axis='x', linestyle='--', alpha=0.5)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label("Luck Score", fontsize=12)

        st.pyplot(fig)

        # -------------------------------
        # STEP 3: Download button
        # -------------------------------
        csv_download = leaderboard.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Leaderboard CSV",
            data=csv_download,
            file_name="fantasy_luck_leaderboard.csv",
            mime="text/csv"
        )

