import streamlit as st
import plotly.express as px

df = st.session_state["df"]

st.title("📈 Business Insights")

# Pareto
st.subheader("Pareto Analysis (80/20 Rule)")

pareto = df.sort_values("Revenue", ascending=False)
pareto["cum"] = pareto["Revenue"].cumsum()
pareto["perc"] = pareto["cum"] / pareto["Revenue"].sum()

fig = px.line(pareto, y="perc")
st.plotly_chart(fig, use_container_width=True)

# Insight otomatis
top_20 = pareto.head(int(len(df)*0.2))["Revenue"].sum()
total = df["Revenue"].sum()

st.success(f"Top 20% products contribute {top_20/total:.2%} of revenue")