import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy,
)
from google.oauth2 import service_account
from django.conf import settings
import logging
from dotenv import load_dotenv
from pathlib import Path

# Force load .env from the project root
env_path = Path(settings.BASE_DIR).parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

def get_google_analytics_stats():
    """
    Fetches real-time statistics from Google Analytics 4 (GA4).
    Returns a dictionary with visits and average position (if available via Search Console linked or similar).
    Since average position in GA4 is tricky, we'll focus on active users and sessions for now.
    """
    property_id = os.environ.get('GA4_PROPERTY_ID')
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    if not property_id or not credentials_path:
        logger.warning("Google Analytics credentials or Property ID missing. Returning placeholder data.")
        return {
            'visits': "12.4K",
            'avg_position': "4.2"
        }

    try:
        # Load credentials from file
        client = BetaAnalyticsDataClient.from_service_account_json(credentials_path)

        # Request 1: Monthly Visits (Sessions in the last 30 days)
        request_sessions = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        )
        response_sessions = client.run_report(request_sessions)
        
        sessions_count = 0
        if response_sessions.rows:
            sessions_count = int(response_sessions.rows[0].metric_values[0].value)

        # Formatting sessions (e.g., 12400 -> 12.4K)
        if sessions_count >= 1000:
            formatted_sessions = f"{sessions_count / 1000:.1f}K"
        else:
            formatted_sessions = str(sessions_count)

        # Request 2: "Avg Position" is usually from Search Console. 
        # In GA4, we can look at "Engaged Sessions" or something else if Search Console isn't linked.
        # For now, let's keep the placeholder or try to fetch a relevant metric if possible.
        # Most users want the placeholder if Search Console is not set up.
        
        return {
            'visits': formatted_sessions,
            'avg_position': "4.2" # Custom logic or Search Console API would be needed for real position
        }

    except Exception as e:
        logger.error(f"Error fetching Google Analytics data: {e}")
        return {
            'visits': "Error",
            'avg_position': "Error"
        }
