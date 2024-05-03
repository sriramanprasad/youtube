import streamlit as st
from pytube import YouTube
import os
import re

# Check and create download directory if needed
download_dir = "downloads"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Set Streamlit app configuration
st.set_page_config(
    page_title="YTD", page_icon="🎞️", layout="wide"
)


@st.cache_data  # Use st.cache_data for caching retrieved video info
def get_info(url):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, type="video")
        details = {}
        details["thumbnail_url"] = yt.thumbnail_url
        details["streams"] = streams
        details["title"] = yt.title
        details["length"] = yt.length / 60  # Convert length to minutes

        # Extract resolutions and itags using regular expressions
        for stream in details["streams"]:
            res_match = re.search(r"(\d+)[p|i]", stream.resolution)
            if res_match:
                stream.resolution = res_match.group(1) + "p"
            details["streams"].append(stream)

        return details
    except Exception as e:
        st.error(f"Error retrieving video info: {e}")
        return None


def main():
    # Title and disclaimer
    st.title("YouTube Downloader ")
    st.markdown(
        ":warning: Downloading copyrighted content without permission might violate terms of service."
    )

    # Input URL and handle errors
    url = st.text_input("Paste URL here ", placeholder="https://www.youtube.com/...")
    if not url:
        return

    # Get video details and handle errors
    details = get_info(url)
    if not details:
        return

    # Display video details and download options
    col1, col2 = st.columns([1, 1.5], gap="small")
    with col1:
        st.image(details["thumbnail_url"])
    with col2:
        st.subheader("Video Details ⚙️")
        st.write(f"Title: {details['title']}")
        st.write(f"Length: {details['length']:.2f} minutes")
        st.write(f"Available Resolutions:")
        for stream in details["streams"]:
            def download_video(stream_):
                # Download function with selected resolution and filename
                filename = st.text_input(f"{stream_.resolution}", key=stream_.itag)
                if filename or filename == details["title"]:
                    try:
                        stream_.download(output_path=download_dir, filename=filename + ".mp4")
                        st.success(f"✅ Downloaded {filename}.mp4!")
                    except Exception as e:
                        st.error(f"Error downloading: {e}")

            # Button to display download options for each resolution
            if st.button(f"{stream.resolution} ({stream.abr // 1000}kbps)", key=stream_.itag):
                download_video(stream)


if __name__ == "__main__":
    main()
