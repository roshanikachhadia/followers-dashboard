import streamlit as st
import pandas as pd
import plotly.express as px

# 1. TITLE
st.title("Multi-Platform Followers Dashboard")

# 2. DATA (Hardcoded)
data = [
    {"creator": "Alice", "platform": "Instagram", "followers": 1500},
    {"creator": "Alice", "platform": "Twitter", "followers": 850},
    {"creator": "Alice", "platform": "TikTok", "followers": 3200},
    {"creator": "Bob", "platform": "Instagram", "followers": 2100},
    {"creator": "Bob", "platform": "Twitter", "followers": 1200},
    {"creator": "Bob", "platform": "TikTok", "followers": 5000},
]
df = pd.DataFrame(data)

# 3. SIDEBAR FILTER
selected_creator = st.sidebar.selectbox("Choose a creator:", df['creator'].unique())
filtered_df = df[df['creator'] == selected_creator]

# 4. KPI CARDS (Top of the page)
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

# Note: We use filtered_df for Total, but df (global) for counts to keep context
total_followers = filtered_df['followers'].sum() 
top_platform = filtered_df.loc[filtered_df['followers'].idxmax(), 'platform']
num_creators = df['creator'].nunique() # Global count
num_platforms = df['platform'].nunique() # Global count

with col1:
    st.metric(label="Total Followers (Selected)", value=total_followers)
with col2:
    st.metric(label="Top Platform", value=top_platform)
with col3:
    st.metric(label="Total Creators in DB", value=num_creators)
with col4:
    st.metric(label="Total Platforms", value=num_platforms)

st.markdown("---") # Adds a nice divider line

# 5. CHART (Middle)
# --- CHARTS SECTION (Side by Side) ---
st.subheader(f"Performance of {selected_creator}")

# Create 2 columns
col_chart1, col_chart2 = st.columns(2)

# 1. Bar Chart (Left Side)
with col_chart1:
    fig_bar = px.bar(
        filtered_df, 
        x='platform', 
        y='followers', 
        color='platform', 
        title='Followers Count'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 2. Pie Chart (Right Side)
with col_chart2:
    fig_pie = px.pie(
        filtered_df, 
        values='followers', 
        names='platform', 
        title='Platform Share (%)'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 6. TABLE (Bottom)
st.subheader("Detailed Data View")
st.dataframe(filtered_df)
