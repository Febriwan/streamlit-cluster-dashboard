import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Product Ranking", layout="wide")
st.title("Peringkat Nilai Pola Produk")

if "df" not in st.session_state:
    st.error("Silakan buka halaman Dashboard terlebih dahulu!")
    st.stop()

df = st.session_state["df"]

col_ctrl1, col_ctrl2 = st.columns([2, 1])
with col_ctrl1:
    top_n = st.slider("Pilih Jumlah Produk Teratas (Top N):", 5, 50, 15)
with col_ctrl2:
    cluster_opt = st.selectbox("Pilih Klaster Spesifik:", ["Semua", 0, 1, 2, 3])

# Filter data berdasarkan klaster terpilih
if cluster_opt != "Semua":
    filtered_df = df[df["Cluster"] == cluster_opt]
else:
    filtered_df = df

top_df = filtered_df.sort_values("Revenue", ascending=False).head(top_n)

fig = px.bar(
    top_df,
    x="Revenue",
    y="Product_Name",
    orientation="h",
    text_auto=".2s",
    title=f"Top {top_n} Produk dengan Utilitas Pendapatan Tertinggi",
    color="Revenue",
    color_continuous_scale="Blues"
)
fig.update_layout(yaxis={'categoryorder':'total ascending'})

st.plotly_chart(fig, use_container_width=True)
st.dataframe(top_df, use_container_width=True)