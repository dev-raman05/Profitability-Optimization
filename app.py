import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Hospitality Revenue & Profitability Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_parquet("big_data_file.parquet")
    return df

df = load_data()

st.title("Optimizing Revenue Leakage & Profitability in the Hospitality Sector")

# Sidebar Filters
st.sidebar.header("Filters")
selected_cities = st.sidebar.multiselect("Select City", df['city'].unique(), default=df['city'].unique())
selected_properties = st.sidebar.multiselect("Select Property", df[df['city'].isin(selected_cities)]['property_name'].unique(), default=df[df['city'].isin(selected_cities)]['property_name'].unique())
selected_room_class = st.sidebar.multiselect("Select Room Class", df['room_class'].unique(), default=df['room_class'].unique())

# Filter data
filtered_df = df[
    (df['city'].isin(selected_cities)) &
    (df['property_name'].isin(selected_properties)) &
    (df['room_class'].isin(selected_room_class))
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# KPIs
st.header("Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)

total_revenue_generated = filtered_df['revenue_generated'].sum()
total_revenue_realized = filtered_df['revenue_realized'].sum()
avg_profitability_index = filtered_df['Profitability_Index'].mean()
avg_rating = filtered_df['ratings_given'].mean()
occupancy_rate = (filtered_df['successful_bookings'].sum() / filtered_df['capacity'].sum()) * 100

col1.metric("Total Revenue Generated", f"₹{total_revenue_generated:,.0f}")
col2.metric("Total Revenue Realized", f"₹{total_revenue_realized:,.0f}")
col3.metric("Avg Profitability Index", f"{avg_profitability_index:.2%}")
col4.metric("Occupancy Rate", f"{occupancy_rate:.2f}%")

st.markdown("---")

# Charts
st.header("Trends & Insights")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Profitability Index by Property")
    prop_pi = filtered_df.groupby('property_name')['Profitability_Index'].mean().reset_index()
    fig1 = px.bar(prop_pi.sort_values(by="Profitability_Index", ascending=False), x='property_name', y='Profitability_Index', color='Profitability_Index', color_continuous_scale='viridis')
    st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("Revenue: Generated vs Realized by Room Class")
    room_rev = filtered_df.groupby('room_class')[['revenue_generated', 'revenue_realized']].sum().reset_index()
    fig2 = px.bar(room_rev, x='room_class', y=['revenue_generated', 'revenue_realized'], barmode='group')
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.subheader("Weekly Profitability Index Trend")
    week_pi = filtered_df.groupby('week no')['Profitability_Index'].mean().reset_index()
    fig3 = px.line(week_pi, x='week no', y='Profitability_Index', markers=True)
    st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("Revenue Realized by City")
    city_rev = filtered_df.groupby('city')['revenue_realized'].sum().reset_index()
    fig4 = px.pie(city_rev, names='city', values='revenue_realized', hole=0.3)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.header("Detailed Data View")
st.dataframe(filtered_df.head(100))
