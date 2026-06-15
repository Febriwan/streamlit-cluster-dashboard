import streamlit as st

df = st.session_state["df"]

st.title(" Product Explorer")

keyword = st.text_input("Search Product")

if keyword:
    result = df[df["Product_Name"].str.contains(keyword, case=False)]

    st.write(f"Found {len(result)} products")

    st.dataframe(result)