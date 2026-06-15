import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("E-Commerce Dashboard")

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    dfs = []
    for i in range(4):
        path = f"data/final_patterns_cluster_{i}.csv"
        try:
            df = pd.read_csv(path)
            df["Cluster"] = i
            dfs.append(df)
        except:
            st.error(f"File tidak ditemukan: {path}")
            st.stop()

    df = pd.concat(dfs)

    # ================= CLEAN REVENUE =================
    df["Revenue"] = (
        df["Revenue"]
        .astype(str)
        .str.replace("£", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)

    return df


df = load_data()
st.session_state["df"] = df

# ================= FILTER =================
cluster = st.selectbox(
    "Pilih Cluster",
    ["All", 0, 1, 2, 3],
    index=0
)

if cluster == "All":
    df_show = df
else:
    df_show = df[df["Cluster"] == cluster]

# ================= METRICS =================
col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"£{df_show['Revenue'].sum():,.0f}")
col2.metric("Total Product", len(df_show))
col3.metric("Avg Revenue", f"£{df_show['Revenue'].mean():,.0f}")

# ================= BAR CHART =================
st.subheader("Top Products")

top = df_show.sort_values("Revenue", ascending=False).head(10)

fig_bar = px.bar(
    top,
    x="Revenue",
    y="Product_Name",
    orientation="h",
    title="Top 10 Product by Revenue"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ================= PIE CHART =================
st.subheader("Distribusi Cluster")

col_pie1, col_pie2 = st.columns(2)

# PIE 1: JUMLAH DATA
cluster_dist = df["Cluster"].value_counts().reset_index()
cluster_dist.columns = ["Cluster", "Count"]

fig_pie1 = px.pie(
    cluster_dist,
    names="Cluster",
    values="Count",
    title="Distribusi Data per Cluster"
)

col_pie1.plotly_chart(fig_pie1, use_container_width=True)

# PIE 2: REVENUE
rev_dist = df.groupby("Cluster")["Revenue"].sum().reset_index()

fig_pie2 = px.pie(
    rev_dist,
    names="Cluster",
    values="Revenue",
    title="Kontribusi Revenue per Cluster"
)

col_pie2.plotly_chart(fig_pie2, use_container_width=True)