import streamlit as st
import plotly.express as px
import pandas as pd

st.title(" Cluster Analysis + HUIM")

# ================= AMBIL DATA =================
if "df" not in st.session_state:
    st.error("Silakan buka Dashboard dulu")
    st.stop()

df = st.session_state["df"].copy()

# ================= FIX DATA =================
df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)

# ================= AGREGASI PER CLUSTER =================
cluster_summary = df.groupby("Cluster").agg({
    "Revenue": ["sum", "mean", "count"]
}).reset_index()

cluster_summary.columns = ["Cluster", "Total Revenue", "Avg Revenue", "Total Product"]

# ================= METRICS GLOBAL =================
st.subheader(" Ringkasan Semua Cluster")

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"£{df['Revenue'].sum():,.0f}")
col2.metric("Total Product", len(df))
col3.metric("Jumlah Cluster", df["Cluster"].nunique())

# ================= BAR CHART =================
st.subheader(" Perbandingan Revenue per Cluster")

fig_bar = px.bar(
    cluster_summary,
    x="Cluster",
    y="Total Revenue",
    text_auto=True,
    title="Total Revenue per Cluster"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ================= PIE CHART =================
st.subheader(" Kontribusi Revenue")

fig_pie = px.pie(
    cluster_summary,
    names="Cluster",
    values="Total Revenue",
    title="Kontribusi Revenue per Cluster"
)

st.plotly_chart(fig_pie, use_container_width=True)

# ================= SCATTER =================
st.subheader(" Distribusi Cluster")

x_col = "Quantity" if "Quantity" in df.columns else None
name_col = "Product_Name" if "Product_Name" in df.columns else None

if x_col is None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ["Cluster", "Revenue"]]
    x_col = numeric_cols[0] if numeric_cols else "Revenue"

fig_scatter = px.scatter(
    df,
    x=x_col,
    y="Revenue",
    color=df["Cluster"].astype(str),
    title=f"Cluster Distribution (X: {x_col}, Y: Revenue)",
    hover_data=[name_col] if name_col else None
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ================= TOP PRODUCT =================
st.subheader(" Top Product per Cluster")

if name_col is None:
    name_col = df.columns[0]

for c in sorted(df["Cluster"].unique()):
    st.markdown(f"### Cluster {c}")
    
    top = df[df["Cluster"] == c] \
        .sort_values("Revenue", ascending=False) \
        .head(5)

    fig = px.bar(
        top,
        x="Revenue",
        y=name_col,
        orientation="h",
        title=f"Top 5 Product Cluster {c}"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= HUIM =================
st.subheader(" High Utility Item (Per Cluster)")

def huim_simple(data, min_util=0.05):
    total_revenue = data["Revenue"].sum()
    threshold = total_revenue * min_util

    hui = data.groupby(name_col)["Revenue"].sum().reset_index()
    hui = hui[hui["Revenue"] >= threshold]

    return hui.sort_values("Revenue", ascending=False)

for c in sorted(df["Cluster"].unique()):
    st.markdown(f"###  HUIM Cluster {c}")

    temp = df[df["Cluster"] == c]

    hui = huim_simple(temp, min_util=0.05)

    if hui.empty:
        st.warning("Tidak ada high utility item")
        continue

    st.dataframe(hui.head(10), use_container_width=True)

    fig = px.bar(
        hui.head(10),
        x="Revenue",
        y=name_col,
        orientation="h",
        title=f"Top High Utility Items Cluster {c}"
    )

    st.plotly_chart(fig, use_container_width=True)