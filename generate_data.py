import pandas as pd
import random
from datetime import datetime, timedelta

# 1. Setup
creators = ['Alice', 'Bob', 'Charlie']
platforms = ['Instagram', 'Twitter', 'TikTok', 'YouTube']
days = 30 # Hum 30 days ka data banayenge

data = []
start_date = datetime(2023, 10, 1)

# 2. Data Generate Karein
for creator in creators:
    for platform in platforms:
        # Har creator/platform ka starting followers alag hoga
        base_followers = random.randint(1000, 5000)
        base_following = random.randint(100, 500)
        base_posts = random.randint(10, 100)
        
        current_followers = base_followers
        for i in range(days):
            # 20% chance ki us din ka data miss ho jaye (Sparse data test)
            if random.random() < 0.2:
                continue 
                
            current_date = start_date + timedelta(days=i)
            
            # Followers thode thode badhenge (random growth)
            growth = random.randint(-50, 150) 
            current_followers += growth
            if current_followers < 0: current_followers = 0 
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'creator': creator,
                'platform': platform,
                'username': f"{creator.lower()}_{platform.lower()}",
                'followers': current_followers,
                'following': base_following + i,
                'posts': base_posts + i
            })

# 3. CSV File Banayein
df = pd.DataFrame(data)
df.to_csv('data/sample_data.csv', index=False)
print("✅ 30 days of sample data generated successfully!")