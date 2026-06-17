import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="Analisis Klaster", layout="wide")
st.title("Analisis Klaster & High Utility Itemset Mining")

if "df" not in st.session_state:
    st.error("Silakan buka halaman Dashboard terlebih dahulu untuk memuat data!")
    st.stop()

df = st.session_state["df"].copy()

# ================= RINGKASAN KLASTER =================
st.subheader("Ringkasan Performa Klaster")
cluster_summary = df.groupby("Cluster").agg({
    "Revenue": ["sum", "mean", "count"]
}).reset_index()
cluster_summary.columns = ["Cluster", "Total Revenue", "Avg Revenue", "Total Product"]

# Perbaikan pada sintaks kurung kurawal format (menghapus spasi)
st.dataframe(cluster_summary.style.format({
    "Total Revenue": "£{:,.2f}",
    "Avg Revenue": "£{:,.2f}"
}), use_container_width=True)

# ================= SEBARAN KLASTER (SCATTER PLOT) =================
st.markdown("---")
st.subheader("Visualisasi Pemisahan Ruang Klaster (Pendapatan vs Itemset ID)")

# Mengubah tipe data Cluster menjadi string agar Plotly Express 
# mewarnai klaster secara kategorikal/diskret (bukan gradasi warna numerik)
df_scatter = df.copy()
df_scatter["Cluster"] = df_scatter["Cluster"].astype(str)

fig_scatter = px.scatter(
    df_scatter, 
    x="Revenue", 
    y="Itemset_ID", 
    color="Cluster",
    title="Sebaran Itemset Berdasarkan Nilai Pendapatan dan ID Klaster",
    labels={"Revenue": "Pendapatan (£)", "Itemset_ID": "Kerapatan Pola (Itemset)", "Cluster": "Klaster"},
    color_discrete_sequence=px.colors.qualitative.Set1
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ================= VISUALISASI RFM CLUSTERING =================
st.subheader("Visualisasi Segmentasi Pelanggan (RFM Clustering)")

try:

    raw_df = pd.read_csv(
        r"data/cleaned_uk_v2.csv"
    )

    # Konversi tanggal
    raw_df["InvoiceDate"] = pd.to_datetime(
        raw_df["InvoiceDate"],
        errors="coerce"
    )

    # Revenue
    raw_df["Revenue"] = (
        raw_df["Quantity"] * raw_df["Price"]
    )

    # Snapshot date
    snapshot_date = (
        raw_df["InvoiceDate"].max()
        + pd.Timedelta(days=1)
    )

    # ================= RFM =================
    rfm_df = raw_df.groupby("Customer ID").agg({
        "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
        "Invoice": "nunique",
        "Revenue": "sum"
    }).reset_index()

    rfm_df.columns = [
        "CustomerID",
        "Recency",
        "Frequency",
        "Monetary"
    ]

    # ================= OUTLIER REMOVAL (TOP 1%) =================

    st.markdown("### Outlier Cleaning (Top 1%)")

    total_before = len(rfm_df)

    freq_cutoff = rfm_df["Frequency"].quantile(0.99)
    monetary_cutoff = rfm_df["Monetary"].quantile(0.99)

    rfm_original = rfm_df.copy()

    rfm_df = rfm_df[
        (rfm_df["Frequency"] <= freq_cutoff) &
        (rfm_df["Monetary"] <= monetary_cutoff)
    ].copy()

    total_after = len(rfm_df)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric(
            "Customer Sebelum Filter",
            total_before
        )

    with col_b:
        st.metric(
            "Customer Setelah Filter",
            total_after
        )

    with col_c:
        st.metric(
            "Outlier Dihapus",
            total_before - total_after
        )

    # ================= VISUALISASI OUTLIER =================

    col_before, col_after = st.columns(2)

    with col_before:

        fig_before = px.box(
            rfm_original,
            y=["Frequency", "Monetary"],
            title="Sebelum Outlier Removal"
        )

        st.plotly_chart(
            fig_before,
            use_container_width=True
        )

    with col_after:

        fig_after = px.box(
            rfm_df,
            y=["Frequency", "Monetary"],
            title="Setelah Outlier Removal (Top 1%)"
        )

        st.plotly_chart(
            fig_after,
            use_container_width=True
        )

    # ================= KMEANS =================
    rfm_log = np.log1p(rfm_df[["Recency", "Frequency", "Monetary"]])
    
    scaler = StandardScaler()
    X = scaler.fit_transform(rfm_log)

    kmeans = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10
    )

    rfm_df["Cluster"] = kmeans.fit_predict(X)
    rfm_df["Cluster"] = rfm_df["Cluster"].astype(str)

    # ================= CHART 1 =================

    col1, col2 = st.columns(2)

    with col1:

        fig_rf = px.scatter(
            rfm_df,
            x="Recency",
            y="Frequency",
            color="Cluster",
            log_y=True,
            opacity=0.7,
            title="Recency vs Frequency",
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        st.plotly_chart(
            fig_rf,
            use_container_width=True
        )

    # ================= CHART 2 =================

    with col2:

        fig_fm = px.scatter(
            rfm_df,
            x="Frequency",
            y="Monetary",
            color="Cluster",
            log_y=True,
            opacity=0.7,
            title="Frequency vs Monetary",
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        st.plotly_chart(
            fig_fm,
            use_container_width=True
        )

    # ================= CHART 3 =================

    fig_rm = px.scatter(
        rfm_df,
        x="Recency",
        y="Monetary",
        color="Cluster",
        log_y=True,
        opacity=0.7,
        title="Recency vs Monetary",
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    st.plotly_chart(
        fig_rm,
        use_container_width=True
    )

    # ================= RINGKASAN RFM =================

    st.markdown("### Ringkasan Segmentasi Pelanggan")

    rfm_summary = (
        rfm_df.groupby("Cluster")
        .agg({
            "CustomerID": "count",
            "Recency": "mean",
            "Frequency": "mean",
            "Monetary": "mean"
        })
        .round(2)
    )

    st.dataframe(
        rfm_summary,
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Gagal membuat visualisasi RFM: {e}"
    )
