import os
import matplotlib.pyplot as plt
import seaborn as sns
from googleapiclient.discovery import build
from textblob import TextBlob

# Function to fetch comments from a YouTube video
def get_video_comments(youtube, video_id, max_comments=100):
    comments = []
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_comments,
        textFormat="plainText"
    ).execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        # Check if there are more comments and continue fetching
        if 'nextPageToken' in response:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=max_comments,
                textFormat="plainText"
            ).execute()
        else:
            break
    return comments

# Function to fetch video IDs from a YouTube channel
def get_channel_videos(api_key, channel_id, max_results=5):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        part='id',
        channelId=channel_id,
        maxResults=max_results,
        order='date',
        type='video'
    )
    response = request.execute()
    video_ids = [item['id']['videoId'] for item in response['items']]
    return video_ids

# Function to analyze sentiment using TextBlob
def analyze_sentiment(comments):
    sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
    sentiment_scores = []

    for comment in comments:
        analysis = TextBlob(comment)
        sentiment_scores.append(analysis.sentiment.polarity)
        # Classify comment as positive, neutral, or negative
        if analysis.sentiment.polarity > 0:
            sentiments['positive'] += 1
        elif analysis.sentiment.polarity == 0:
            sentiments['neutral'] += 1
        else:
            sentiments['negative'] += 1

    return sentiments, sentiment_scores

# Function to plot sentiment analysis results
def plot_sentiment_results(sentiments, sentiment_scores):
    # Bar plot of sentiment categories
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(sentiments.keys()), y=list(sentiments.values()))
    plt.title("Sentiment Distribution of YouTube Comments")
    plt.ylabel("Number of Comments")
    plt.xlabel("Sentiment")
    plt.show()

    # Histogram of sentiment polarity scores
    plt.figure(figsize=(10, 6))
    sns.histplot(sentiment_scores, kde=True, bins=20)
    plt.title("Sentiment Polarity Scores of YouTube Comments")
    plt.xlabel("Polarity Score")
    plt.ylabel("Frequency")
    plt.show()

# Main function to fetch comments, analyze sentiment, and visualize
def main(api_key, channel_id, max_results=5, max_comments=100):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Fetch video IDs from the channel
    video_ids = get_channel_videos(api_key, channel_id, max_results)
    all_comments = []

    # Fetch comments from each video
    for video_id in video_ids:
        print(f"Fetching comments for video ID: {video_id}")
        comments = get_video_comments(youtube, video_id, max_comments)
        all_comments.extend(comments)

    # Perform sentiment analysis on the comments
    sentiments, sentiment_scores = analyze_sentiment(all_comments)

    # Plot the results
    plot_sentiment_results(sentiments, sentiment_scores)

if __name__ == "__main__":
    # Replace with your YouTube API key and channel ID
    YOUTUBE_API_KEY = "your-api-key"
    CHANNEL_ID = "your-youtube-channel-id"
    
    main(YOUTUBE_API_KEY, CHANNEL_ID)
