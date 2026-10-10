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
st.caption("️ Note: This dashboard uses synthetic sample data for demonstration purposes.")

# 2. LOAD DATA
df = pd.read_csv("data/sample_data.csv")
# 2. LOAD DATA
df = pd.read_csv("data/sample_data.csv")

# Convert 'date' column to actual datetime objects
df['date'] = pd.to_datetime(df['date'])
# Sort data so calculations are correct
df = df.sort_values(by=['creator', 'platform', 'date']).reset_index(drop=True)
# Platform names ko emojis ke sath map karna
platform_icons = {
    'Instagram': '📸 Instagram',
    'Twitter': ' Twitter',
    'TikTok': '🎵 TikTok',
    'YouTube': '▶️ YouTube'
}

# DataFrame ke 'platform' column mein purane naam ko naye naam se replace karna
df['platform'] = df['platform'].replace(platform_icons)

# --- CREATOR SELECTOR (Ab 2 tak chun sakte hain) ---
selected_creators = st.sidebar.multiselect(
    "Choose creators (max 2):",
    options=df['creator'].unique(),
    default=[df['creator'].unique()[0]], # Pehla creator default rahega
    max_selections=2
)
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
# --- Date Range Selector ---
# Get the earliest and latest dates from our data
min_date = df['date'].min().date()
max_date = df['date'].max().date()

# Create the date picker
selected_dates = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date), # Default: show full history
    min_value=min_date,
    max_value=max_date
)
# Convert selected dates to Pandas Timestamps (taaki error na aaye)
start_date = pd.Timestamp(selected_dates[0])
end_date = pd.Timestamp(selected_dates[1])
# Filter by creator, platform, followers, AND date range
filtered_df = df[
    (df['creator'].isin(selected_creators)) &  
    (df['platform'].isin(selected_platforms)) & 
    (df['followers'] >= selected_range[0]) & 
    (df['date'] >= start_date) &  
    (df['date'] <= end_date)  
]
# --- CALCULATE ABSOLUTE GROWTH ---
# Group by platform to find first and last followers in the selected range
growth_df = filtered_df.groupby('platform').agg(
    earliest_followers=('followers', 'first'),
    latest_followers=('followers', 'last')
).reset_index()

# Calculate the difference
growth_df['absolute_growth'] = growth_df['latest_followers'] - growth_df['earliest_followers']
# --- CALCULATE GROWTH PERCENTAGE ---
def safe_growth_pct(row):
    # Agar shuru mein 0 followers the, toh 0 return kar do (Error se bachne ke liye)
    if row['earliest_followers'] == 0:
        return 0.0
    # Warna normal formula lagao: (Latest - Earliest) / Earliest * 100
    return ((row['latest_followers'] - row['earliest_followers']) / row['earliest_followers']) * 100

# Is function ko har row par apply karo
growth_df['growth_percentage'] = growth_df.apply(safe_growth_pct, axis=1)
# 5. HANDLE EMPTY DATA (IF-ELSE)
if len(filtered_df) == 0:
    st.warning("⚠️ No data found for this selection! Please adjust your filters.")
    

else:
    # --- KPI CARDS ---
        # Calculations
    total_followers = filtered_df['followers'].sum()
     # Saare selected platforms ki growth ko jod do
    total_growth = growth_df['absolute_growth'].sum()

        # Total growth percentage calculate karo
    total_earliest = growth_df['earliest_followers'].sum()
    total_latest = growth_df['latest_followers'].sum()

    if total_earliest > 0:
            total_growth_pct = ((total_latest - total_earliest) / total_earliest) * 100
    else:
            total_growth_pct = 0.0
                # Sabse zyada growth percentage wali row dhundho aur uska platform naam nikalo
    fastest_platform = growth_df.loc[growth_df['growth_percentage'].idxmax(), 'platform']
        # Find the latest date in the filtered data
    latest_date = filtered_df['date'].max()

    # Get total followers for that latest date
    current_followers = filtered_df[filtered_df['date'] == latest_date]['followers'].sum()
    top_platform = filtered_df.loc[filtered_df['followers'].idxmax(), 'platform']
    num_creators = df['creator'].nunique()
    num_platforms = df['platform'].nunique()
        # First row of KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Current Followers", value=format_number(current_followers))
    with col2:
        st.metric(label="Top Platform", value=top_platform)
    with col3:
        st.metric(label="Total Creators in DB", value=num_creators)
    with col4:
        st.metric(label="Total Platforms", value=num_platforms)
    
    # Second row for growth metrics
    col5, col6 = st.columns(2)
     # Agar aapke paas col7 nahi hai, toh ek naya row bana lo ya kisi purane col mein daal do
    with col5: # Ya koi bhi available column
        st.metric(label="Fastest Growing Platform", value=fastest_platform)
    
    with col5:
        st.metric(label="Followers Gained", value=total_growth)
    with col6:
        # :.1f ka matlab hai number ke baad sirf 1 digit dikhao (e.g., 12.5%)
        st.metric(label="Growth Percentage", value=f"{total_growth_pct:.1f}%")  # Agar aapne percentage bhi calculate kiya hai
# Show growth table
    st.subheader("Platform Growth in Selected Period")
    st.dataframe(growth_df, hide_index=True, use_container_width=True)
    # --- CHARTS SECTION ---
    st.subheader(f"Performance of {', '.join(selected_creators)}")
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
    # --- CREATOR COMPARISON CHART ---
    if len(selected_creators) > 1:
        st.subheader("Creator vs Creator Comparison")
        
        # Dono creators ke total followers nikalo
        comparison_data = filtered_df.groupby('creator')['followers'].sum().reset_index()
        
        fig_compare = px.bar(
            comparison_data, 
            x='creator', 
            y='followers', 
            color='creator', 
            title='Total Followers Comparison'
        )
        st.plotly_chart(fig_compare, use_container_width=True)
        # --- LINE CHART SECTION ---
    st.subheader("Follower Growth Over Time")
    
    fig_line = px.line(
        filtered_df, 
        x='date', 
        y='followers', 
        color='platform',  # Yeh line har platform ka alag color banayegi
        markers=True,      # Yeh line par chote dots dikhayegi
        title='Followers Growth by Platform'
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # --- TABLE SECTION ---
    st.subheader("Detailed Data View")
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)
