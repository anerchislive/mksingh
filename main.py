import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz
from utils.news_fetcher import NewsFetcher
from utils.ml_sentiment_analyzer import MLSentimentAnalyzer

# Page config
st.set_page_config(
    page_title="Stock News Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def get_components():
    return NewsFetcher(), MLSentimentAnalyzer()  # Using ML Sentiment Analyzer

news_fetcher, sentiment_analyzer = get_components()

def load_data():
    try:
        # Read symbols, skip first row
        symbols = news_fetcher.read_symbols('attached_assets/MW-SECURITIES-IN-F&O-28-Feb-2025.csv')[1:]
        news_data = []

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, symbol in enumerate(symbols):
            try:
                progress = (i + 1) / len(symbols)
                progress_bar.progress(progress)
                status_text.text(f'Fetching news for {symbol}...')

                news = news_fetcher.get_news_for_symbol(symbol)
                if news:
                    sentiment, score = sentiment_analyzer.analyze_sentiment(news['title'])
                    # Parse and store timestamp for sorting
                    published_dt = datetime.strptime(news['published_date'], '%a, %d %b %Y %H:%M:%S GMT')
                    published_dt = published_dt.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Asia/Kolkata'))

                    news_data.append({
                        'Symbol': symbol,
                        'Sentiment': sentiment,
                        'Score': score,
                        'Headline': news['title'],
                        'Published': published_dt.strftime('%Y-%m-%d %I:%M %p IST'),
                        'Timestamp': published_dt,  # Store for sorting
                        'URL': news['url']
                    })
            except Exception as symbol_error:
                st.error(f"Error processing symbol {symbol}: {str(symbol_error)}")
                continue

        progress_bar.empty()
        status_text.empty()

        # Create DataFrame and sort by timestamp
        df = pd.DataFrame(news_data)
        if not df.empty:
            df = df.sort_values('Timestamp', ascending=False)
            df = df.drop('Timestamp', axis=1)  # Remove timestamp column after sorting

        return df

    except Exception as e:
        st.error(f"Error in load_data: {str(e)}")
        return pd.DataFrame()

def format_table(df):
    try:
        # Make headlines clickable with separate link
        def make_clickable(row):
            return f'{row["Headline"]} <a href="{row["URL"]}" target="_blank">[Link]</a>'

        df['Headline'] = df.apply(make_clickable, axis=1)

        # Drop URL column and format score
        display_df = df.drop('URL', axis=1).copy()

        # Ensure score is numeric and format it
        display_df['Score'] = pd.to_numeric(display_df['Score'], errors='coerce')

        # Create styled dataframe with ML-based sentiment colors
        styled_df = display_df.style.format({
            'Score': '{:,.2f}'
        }).apply(lambda x: [
            f'background-color: {sentiment_analyzer.get_sentiment_color(x["Sentiment"])}'
            if col == 'Sentiment' else ''
            for col in x.index
        ], axis=1)

        return styled_df
    except Exception as e:
        st.error(f"Error in format_table: {str(e)}")
        return df

# Main app
st.title('📈 Stock News Dashboard')
st.markdown('_Auto-refreshes every 60 seconds_')

# Initialize session state for data caching
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'news_data' not in st.session_state:
    st.session_state.news_data = None

try:
    # Check if we need to update data
    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    if (st.session_state.last_update is None or 
        (current_time - st.session_state.last_update.replace(tzinfo=pytz.timezone('Asia/Kolkata'))).seconds >= 60):

        # Load and display data
        st.session_state.news_data = load_data()
        st.session_state.last_update = current_time

        # Display last updated time
        st.markdown(
            f'<p class="last-updated">Last updated: {current_time.strftime("%Y-%m-%d %I:%M %p IST")}</p>',
            unsafe_allow_html=True
        )

        # Display the news table
        if not st.session_state.news_data.empty:
            st.dataframe(
                format_table(st.session_state.news_data),
                use_container_width=True,
                height=800  # Increased height for better visibility
            )
        else:
            st.warning("No news data available yet. Please wait for the next update.")

except Exception as e:
    st.error(f"An error occurred in main loop: {str(e)}")
    if st.button('Retry'):
        st.experimental_rerun()

# Client-side auto-refresh
st.markdown(
    """
    <script>
        function reloadPage() {
            setTimeout(function() {
                window.location.reload();
            }, 60000);
        }
        reloadPage();
    </script>
    """,
    unsafe_allow_html=True
)