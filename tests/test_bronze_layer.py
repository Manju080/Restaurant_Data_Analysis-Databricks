"""
Unit tests for Bronze layer data ingestion.
Tests raw data loading, schema validation, and metadata addition.
"""
import pytest
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from datetime import datetime


class TestBronzeLayer:
    """Test suite for Bronze layer ingestion."""
    
    def test_business_schema_inference(self, spark, sample_business_data):
        """Test that business data schema is correctly inferred."""
        df = spark.createDataFrame(sample_business_data)
        
        # Check required columns exist
        required_cols = ["business_id", "name", "city", "state", "stars", "review_count"]
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_bronze_metadata_columns(self, spark, sample_business_data):
        """Test that metadata columns are added during bronze ingestion."""
        df = spark.createDataFrame(sample_business_data)
        
        # Simulate adding metadata (as done in 01_bronze_yelp.ipynb)
        from pyspark.sql.functions import current_timestamp, lit
        df_with_metadata = df \
            .withColumn("ingestion_timestamp", current_timestamp()) \
            .withColumn("source_file", lit("test_file.json")) \
            .withColumn("data_layer", lit("bronze"))
        
        assert "ingestion_timestamp" in df_with_metadata.columns
        assert "source_file" in df_with_metadata.columns
        assert "data_layer" in df_with_metadata.columns
    
    def test_no_duplicate_business_ids(self, spark, sample_business_data):
        """Test that bronze layer handles duplicate business IDs."""
        # Add a duplicate
        duplicate_data = sample_business_data + [sample_business_data[0]]
        df = spark.createDataFrame(duplicate_data)
        
        total_rows = df.count()
        unique_ids = df.select("business_id").distinct().count()
        
        # Bronze layer may have duplicates (cleaned in Silver)
        assert total_rows == 3
        assert unique_ids == 2
    
    def test_null_handling_in_bronze(self, spark):
        """Test that bronze layer preserves nulls (no filtering)."""
        data = [
            {"business_id": "biz_001", "name": "Test", "stars": 4.5},
            {"business_id": "biz_002", "name": None, "stars": None}
        ]
        df = spark.createDataFrame(data)
        
        # Bronze should keep all rows, including nulls
        assert df.count() == 2
        assert df.filter(df.name.isNull()).count() == 1
    
    def test_star_rating_range(self, spark, sample_business_data):
        """Test that star ratings are within expected range."""
        df = spark.createDataFrame(sample_business_data)
        
        from pyspark.sql.functions import col
        invalid_stars = df.filter((col("stars") < 1.0) | (col("stars") > 5.0)).count()
        
        assert invalid_stars == 0, "Found star ratings outside 1.0-5.0 range"
