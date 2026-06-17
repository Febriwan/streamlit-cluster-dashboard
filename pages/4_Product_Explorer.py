import streamlit as st

st.set_page_config(page_title="Product Explorer", layout="wide")
st.title("Penjelajah & Pencarian Produk")

if "df" not in st.session_state:
    st.error("Silakan buka halaman Dashboard terlebih dahulu!")
    st.stop()

df = st.session_state["df"]

keyword = st.text_input("Ketik Nama Produk atau Kata Kunci (Contoh: HEART, BAG, CAKESTAND):")

if keyword:
    result = df[df["Product_Name"].str.contains(keyword, case=False, na=False)]
    
    st.markdown(f"### Hasil Pencarian Untuk: *'{keyword}'*")
    
    # Metrik Ringkas Hasil Pencarian
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    sub_col1.metric("Jumlah Produk Ditemukan", len(result))
    sub_col2.metric("Total Kontribusi Pendapatan", f"£{result['Revenue'].sum():,.2f}")
    sub_col3.metric("Klaster Terkait", ", ".join(list(result["Cluster"].unique().astype(str))))
    
    st.markdown("---")
    st.dataframe(result.sort_values("Revenue", ascending=False), use_container_width=True)
else:
    st.info("Silakan masukkan kata kunci di atas untuk melacak posisi klaster dan kontribusi revenue produk.")