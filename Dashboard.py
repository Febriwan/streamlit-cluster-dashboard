import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="E-Commerce Analytics Dashboard", layout="wide")

st.title("E-Commerce Data Mining Dashboard")
st.markdown("---")

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
        except Exception as e:
            st.error(f"File tidak ditemukan atau rusak: {path}. Error: {e}")
            st.stop()

    df = pd.concat(dfs, ignore_index=True)

    # ================= CLEAN REVENUE DENGAN REGEX =================
    # Menghapus semua karakter kecuali angka dan titik desimal
    df["Revenue"] = df["Revenue"].astype(str).str.replace(r"[^\d.]", "", regex=True)
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)

    return df

df = load_data()
st.session_state["df"] = df

# ================= FILTER CLUSTER =================
cluster = st.selectbox(
    "Filter Berdasarkan Klaster:",
    ["Semua Klaster (All)", 0, 1, 2, 3],
    index=0
)

if cluster == "Semua Klaster (All)":
    df_show = df
else:
    df_show = df[df["Cluster"] == cluster]

# ================= KARTU METRIK =================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pendapatan", f"£{df_show['Revenue'].sum():,.2f}")
with col2:
    st.metric("Total Pola Produk", len(df_show))
with col3:
    st.metric("Rata-rata Pendapatan per Pola", f"£{df_show['Revenue'].mean():,.2f}")

st.markdown("---")

# ================= VISUALISASI UTAMA =================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Produk Berdasarkan Pendapatan")
    top = df_show.sort_values("Revenue", ascending=False).head(10)
    fig_bar = px.bar(
        top,
        x="Revenue",
        y="Product_Name",
        orientation="h",
        labels={"Revenue": "Pendapatan (£)", "Product_Name": "Nama Produk"},
        title="10 Produk Teratas",
        color="Revenue",
        color_continuous_scale="Viridis"
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Distribusi Kontribusi Klaster")
    # Agregasi untuk pie chart pendapatan
    revenue_dist = df.groupby("Cluster")["Revenue"].sum().reset_index()
    fig_pie = px.pie(
        revenue_dist,
        values="Revenue",
        names="Cluster",
        title="Kontribusi Pendapatan per Klaster",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_pie, use_container_width=True)