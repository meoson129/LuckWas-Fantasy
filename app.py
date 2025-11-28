import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fantasy League Luck Dashboard", layout="wide")

st.title("Fantasy League Luck Dashboard")
st.markdown("""
Upload a CSV file containing your league data with the following columns:
- `Team`: Team name
- `PF`: Points For
- `PA`: Points Against

The app will calculate Expected PA, Luck Score, rank teams from Luckiest → Unluckiest,
and display a modern interactive Luck Score chart.
""")

# -------------------------------
# File uploader
# -------------------------------
uploaded_file = st.file_uploader("Upload your league CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in ["Team", "PF", "PA"]):
        st.error("CSV must contain columns: Team, PF, PA")
    else:
        # -------------------------------
        # Calculate Expected PA and Luck Score
        # -------------------------------
        N = len(df)
        df["PF"] = pd.to_numeric(df["PF"], errors='coerce')
        df["PA"] = pd.to_numeric(df["PA"], errors='coerce')
        df["Expected_PA"] = [(df["PF"].sum() - pf)/(N-1) for pf in df["PF"]]

        # Round numeric columns safely
        numeric_cols = ["PF", "PA", "Expected_PA"]
        for col in numeric_cols:
            df[col] = df[col].round(2)

        df["Luck_Score"] = (df["Expected_PA"] - df["PA"]).round(2)
        df = df.sort_values("Luck_Score", ascending=False).reset_index(drop=True)
        df["Luck_Rank"] = range(1, len(df)+1)

        leaderboard = df[["Luck_Rank", "Team", "PF", "PA", "Expected_PA", "Luck_Score"]]
        leaderboard = leaderboard.rename(columns={
            "PF": "Real PF",
            "PA": "Real PA",
            "Expected_PA": "Expected PA"
        })

        # -------------------------------
        # Plotly Bar Chart for Luck Score
        # -------------------------------
        st.header("📊 Luck Score Visualization")
        fig = px.bar(
            leaderboard,
            y="Team",
            x="Luck_Score",
            orientation="h",
            text="Luck_Score",
            color="Luck_Score",
            color_continuous_scale="RdYlGn",
            title="Fantasy League Luck Leaderboard (Luckiest → Unluckiest)"
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis_title="Luck Score (Expected PA - Real PA)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, width="stretch")  # Updated for Streamlit deprecation

        # -------------------------------
        # Display Leaderboard Table
        # -------------------------------
        st.header("📋 Leaderboard Table")
        st.dataframe(
            leaderboard.style.background_gradient(subset=["Luck_Score"], cmap="RdYlGn")
        )

        # -------------------------------
        # Download CSV button
        # -------------------------------
        csv_download = leaderboard.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Leaderboard CSV",
            data=csv_download,
            file_name="fantasy_luck_leaderboard.csv",
            mime="text/csv"
        )

else:
    st.info("Upload a CSV file to get started.")
