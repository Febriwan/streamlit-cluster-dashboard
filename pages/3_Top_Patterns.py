import streamlit as st
import plotly.express as px

df = st.session_state["df"]

st.title(" Product Ranking")

top_n = st.slider("Top N", 5, 50, 15)

top_df = df.sort_values("Revenue", ascending=False).head(top_n)

fig = px.bar(
    top_df,
    x="Revenue",
    y="Product_Name",
    orientation="h",
    text="Revenue"
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(top_df)