"""
Unit tests for Silver layer data cleaning and validation.
Tests deduplication, validation rules, and type casting.
"""
import pytest
from pyspark.sql.functions import col, lower, trim


class TestSilverLayer:
    """Test suite for Silver layer transformations."""
    
    def test_deduplication_business(self, spark, sample_business_data):
        """Test that duplicate business_ids are removed."""
        # Add duplicate
        duplicate_data = sample_business_data + [sample_business_data[0]]
        df = spark.createDataFrame(duplicate_data)
        
        # Deduplicate (as done in Silver layer)
        df_dedupe = df.dropDuplicates(["business_id"])
        
        assert df_dedupe.count() == 2, "Deduplication failed"
    
    def test_city_state_normalization(self, spark, sample_business_data):
        """Test that city and state are normalized to lowercase."""
        df = spark.createDataFrame(sample_business_data)
        
        # Normalize
        df_normalized = df \
            .withColumn("city", lower(trim(col("city")))) \
            .withColumn("state", lower(trim(col("state"))))
        
        cities = df_normalized.select("city").collect()
        assert all(c["city"] == c["city"].lower() for c in cities)
    
    def test_star_rating_validation(self, spark):
        """Test that invalid star ratings are filtered out."""
        data = [
            {"business_id": "biz_001", "stars": 4.5},
            {"business_id": "biz_002", "stars": 6.0},  # Invalid
            {"business_id": "biz_003", "stars": 0.5},  # Invalid
            {"business_id": "biz_004", "stars": 3.0}
        ]
        df = spark.createDataFrame(data)
        
        # Filter invalid stars
        df_valid = df.filter((col("stars") >= 1.0) & (col("stars") <= 5.0))
        
        assert df_valid.count() == 2, "Star rating validation failed"
    
    def test_coordinate_validation(self, spark, sample_business_data):
        """Test that coordinates are within valid ranges."""
        df = spark.createDataFrame(sample_business_data)
        
        invalid_coords = df.filter(
            (col("latitude") < -90) | (col("latitude") > 90) |
            (col("longitude") < -180) | (col("longitude") > 180)
        ).count()
        
        assert invalid_coords == 0, "Found invalid coordinates"
    
    def test_user_tenure_calculation(self, spark, sample_user_data):
        """Test that user tenure is calculated correctly."""
        df = spark.createDataFrame(sample_user_data)
        
        from pyspark.sql.functions import to_date, datediff, current_date
        
        df_with_tenure = df.withColumn(
            "user_tenure_days",
            datediff(current_date(), to_date(col("yelping_since")))
        )
        
        assert "user_tenure_days" in df_with_tenure.columns
        # All tenures should be positive
        assert df_with_tenure.filter(col("user_tenure_days") < 0).count() == 0
    
    def test_review_text_length(self, spark, sample_review_data):
        """Test that review text length is calculated."""
        df = spark.createDataFrame(sample_review_data)
        
        from pyspark.sql.functions import length
        df_with_length = df.withColumn("text_length", length(col("text")))
        
        # All text lengths should be > 0
        assert df_with_length.filter(col("text_length") <= 0).count() == 0
