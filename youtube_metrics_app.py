import streamlit as st # Import Streamlit for the web interface
from googleapiclient.discovery import build #Import Google's YouTube API Client
import re
import matplotlib.pyplot as plt

class YouTubeChannelStats: # Define a class for interacting with the YouTube API
    def __init__(self, api_key):
        # Initialize with your API key and create a Youtube API service object
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        
    def extract_channel_identifier(self, url_or_handle):
        # Extracts identifier (handle or ID) from URL or raw handle
        if "youtube.com/channel/" in url_or_handle:
            return url_or_handle.split("youtube.com/channel/")[1].split("/")[0]
        elif "youtube.com/@":
            return url_or_handle.split("youtube.com/@")[-1].split("/")[0]
        elif url_or_handle.startswith("@"):
            return url_or_handle[1:]  # remove @
        else:
            return url_or_handle.strip()
        
    def get_channel_id_from_handle(self, handle_or_url):
        # Convert handle to channnel ID via API search
        query = self.extract_channel_identifier(handle_or_url)
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        if response ["items"]:
            return response["items"][0]["snippet"]["channelId"]
        else:
            return None
        
    def get_channel_stats(self, channel_id):
        # Make an API request to get channel statistics and snippet
        request = self.youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        )
        response = request.execute()
        
        # Check if the response contains channel data
        if "items" in response and response["items"]:
            data = response['items'][0]
            return {
                'Channel Name': data['snippet']['title'],
                'Subscribers': int(data['statistics']['subscriberCount']),
                'Views': int(data['statistics']['viewCount']),
                'Videos': int(data['statistics']['videoCount']),
            }
        else:
            return None

# Streamlit Web UI

st.set_page_config(page_title="📊 YouTube Channel Metrics Estimator", layout="centered") # Set page configuration

st.title("📊 YouTube Channel Metrics Estimator") # App title

api_key = "AIzaSyDBoNnwit8lCNEQyuJF8ne2Ap4q35iiJ2Q" # Load your API Key from secrets

yt = YouTubeChannelStats(api_key) # Create instance of YouTubeChannelStats

user_input = st.text_input("Enter YouTube Channel Handle or URL (e.g., @MrBeast or https://youtube.com/@MrBeast):") # Input: Handle or URL

# Demogaphic Data

demographic_data = {
    "viewer_gender": {"Male": 62, "Female": 38},
    "viewer_age_groups": {
        "13-17": 5,
        "18-24": 25,
        "25-34": 35,
        "35-44": 20,
        "45-54": 10,
        "55+": 5
    },
    "top_locations": {
        "United States": 40,
        "India": 25,
        "United Kingdom": 15,
        "Nigeria": 10,
        "Canada": 10
    }
} # This is a Simulated Data

# When button is clicked

if st.button("Get Stats") and user_input:
    channel_id = yt.get_channel_id_from_handle(user_input)
    
    if channel_id:
        stats = yt.get_channel_stats(channel_id)
        
        if stats:
            # Display channel data
            st.subheader("📈 Channel Statistics")
            st.markdown(f"**Channel Name:** {stats['Channel Name']}")
            st.markdown(f"**Subscribers:** {stats['Subscribers']:,}")
            st.markdown(f"**Total Views:** {stats['Views']:,}")
            st.markdown(f"**Total Videos:** {stats['Videos']:,}")
            
            st.divider()
            
            # Earnings Estimator
            
            st.subheader("💰 Estimated Monthly Earnings")
            cpm = st.slider("Choose CPM ($)", min_value=1, max_value=25, value=5)
            monthly_views = stats['Views'] // 12
            estimated_earnings = (monthly_views / 1000) * cpm
            st.markdown(f"**Estimated Monthly Earnings:** ${estimated_earnings:,.2f} USD")
            
            # Viewers Demographics and Geography
            st.subheader("🌍 Viewer Demographics & Geography")
            
            #Gender Pie Chart
            fig1, ax1 = plt.subplots()
            ax1.pie(demographic_data["viewer_gender"].values(), labels=demographic_data["viewer_gender"].keys(), autopct='%1.1f%%')
            ax1.set_title("Viewer Gender Distribution")
            st.pyplot(fig1)
            
            # Age Group Bar Chart
            fig2, ax2 = plt.subplots()
            ax2.bar(demographic_data["viewer_age_groups"].keys(), demographic_data["viewer_age_groups"].values())
            ax2.set_title("Viewer Age Groups (%)")
            ax2.set_xlabel("Age Group")
            ax2.set_ylabel("Percentage")
            plt.xticks(rotation=45)
            st.pyplot(fig2)
            
            # Top Locations Pie Chart
            fig3, ax3 = plt.subplots()
            ax3.pie(demographic_data["top_locations"].values(), labels=demographic_data["top_locations"].keys(), autopct='%1.1f%%')
            ax3.set_title("Top Viewer Locations")
            st.pyplot(fig3) 
        else:
            st.error("⚠️ Channel statistics could not be retrieved.")
    else:
        st.error("❌ Could not find a valid YouTube channel from the input.")
