"""
Pytest configuration and shared fixtures for Yelp Churn Prediction tests.
"""
import pytest
from pyspark.sql import SparkSession
from datetime import datetime


@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for testing."""
    spark = SparkSession.builder \
        .appName("yelp-churn-tests") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    
    yield spark
    
    spark.stop()


@pytest.fixture(scope="session")
def catalog_name():
    """Return the test catalog name."""
    return "yelp_dataset_test"


@pytest.fixture(scope="session")
def sample_business_data():
    """Sample business data for testing."""
    return [
        {
            "business_id": "biz_001",
            "name": "Test Restaurant",
            "city": "Phoenix",
            "state": "AZ",
            "stars": 4.5,
            "review_count": 100,
            "is_open": 1,
            "latitude": 33.4484,
            "longitude": -112.0740
        },
        {
            "business_id": "biz_002",
            "name": "Another Cafe",
            "city": "Scottsdale",
            "state": "AZ",
            "stars": 3.5,
            "review_count": 50,
            "is_open": 1,
            "latitude": 33.4942,
            "longitude": -111.9261
        }
    ]


@pytest.fixture(scope="session")
def sample_user_data():
    """Sample user data for testing."""
    return [
        {
            "user_id": "user_001",
            "name": "John Doe",
            "review_count": 50,
            "yelping_since": "2015-01-01",
            "average_stars": 4.2,
            "fans": 10
        },
        {
            "user_id": "user_002",
            "name": "Jane Smith",
            "review_count": 200,
            "yelping_since": "2010-06-15",
            "average_stars": 3.8,
            "fans": 45
        }
    ]


@pytest.fixture(scope="session")
def sample_review_data():
    """Sample review data for testing."""
    return [
        {
            "review_id": "rev_001",
            "user_id": "user_001",
            "business_id": "biz_001",
            "stars": 5,
            "text": "Great food! Highly recommend.",
            "date": "2024-01-15"
        },
        {
            "review_id": "rev_002",
            "user_id": "user_002",
            "business_id": "biz_002",
            "stars": 3,
            "text": "Average experience, nothing special.",
            "date": "2024-02-20"
        }
    ]
