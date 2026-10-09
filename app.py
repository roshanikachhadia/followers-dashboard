import streamlit as st
import pandas as pd
import plotly.express as px
# --- HELPER FUNCTION ---
def format_number(num):
    """Converts large numbers to K or M format."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.0f}K"
    else:
        return str(num)

# 1. TITLE
st.title("Multi-Platform Followers Dashboard")

# 2. LOAD DATA
df = pd.read_csv("data/sample_data.csv")
# Platform names ko emojis ke sath map karna
platform_icons = {
    'Instagram': '📸 Instagram',
    'Twitter': ' Twitter',
    'TikTok': '🎵 TikTok',
    'YouTube': '▶️ YouTube'
}

# DataFrame ke 'platform' column mein purane naam ko naye naam se replace karna
df['platform'] = df['platform'].replace(platform_icons)

# 3. SIDEBAR FILTERS
selected_creator = st.sidebar.selectbox("Choose a creator:", df['creator'].unique())

selected_platforms = st.sidebar.multiselect(
    "Choose platforms:", 
    df['platform'].unique(), 
    default=df['platform'].unique()
)

min_followers = int(df['followers'].min())
max_followers = int(df['followers'].max())

selected_range = st.sidebar.slider(
    "Filter by follower count:",
    min_value=min_followers,
    max_value=max_followers,
    value=(min_followers, max_followers),
    key="follower_slider"
)

# 4. APPLY FILTERS
filtered_df = df[
    (df['creator'] == selected_creator) & 
    (df['platform'].isin(selected_platforms)) & 
    (df['followers'] >= selected_range[0]) & 
    (df['followers'] <= selected_range[1])
]

# 5. HANDLE EMPTY DATA (IF-ELSE)
if len(filtered_df) == 0:
    st.warning("⚠️ No data found for this selection! Please adjust your filters.")

else:
    # --- KPI CARDS ---
        # Calculations
    total_followers = filtered_df['followers'].sum()
    top_platform = filtered_df.loc[filtered_df['followers'].idxmax(), 'platform']
    num_creators = df['creator'].nunique()
    num_platforms = df['platform'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Yahan format_number lagao!
        st.metric(label="Total Followers (Selected)", value=format_number(total_followers))
    with col2:
        st.metric(label="Top Platform", value=top_platform)
    with col3:
        st.metric(label="Total Creators in DB", value=num_creators)
    with col4:
        st.metric(label="Total Platforms", value=num_platforms)    # Calculations

    # --- CHARTS SECTION ---
    st.subheader(f"Performance of {selected_creator}")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_bar = px.bar(
            filtered_df, 
            x='platform', 
            y='followers', 
            color='platform', 
            hover_data=['username'],
            title='Followers Count'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        fig_pie = px.pie(
            filtered_df, 
            values='followers', 
            names='platform', 
            title='Platform Share (%)',
            hole=0.4  # <-- Yeh line add karni hai!
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # --- TABLE SECTION ---
    st.subheader("Detailed Data View")
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)
