"""
Unit tests for Gold layer feature engineering.
Tests feature creation, aggregations, and RFM scoring.
"""
import pytest
from pyspark.sql.functions import col, count, avg, sum as spark_sum, max as spark_max


class TestGoldLayer:
    """Test suite for Gold layer feature engineering."""
    
    def test_business_aggregations(self, spark, sample_review_data):
        """Test that business-level aggregations are correct."""
        df = spark.createDataFrame(sample_review_data)
        
        business_agg = df.groupBy("business_id").agg(
            count("review_id").alias("total_reviews"),
            avg("stars").alias("avg_rating")
        )
        
        assert business_agg.count() == 2  # 2 unique businesses
        assert "total_reviews" in business_agg.columns
        assert "avg_rating" in business_agg.columns
    
    def test_user_review_frequency(self, spark, sample_user_data):
        """Test user review frequency calculation."""
        df = spark.createDataFrame(sample_user_data)
        
        from pyspark.sql.functions import to_date, datediff, current_date
        
        df_with_freq = df.withColumn(
            "user_tenure_days",
            datediff(current_date(), to_date(col("yelping_since")))
        ).withColumn(
            "reviews_per_day",
            col("review_count") / col("user_tenure_days")
        )
        
        assert "reviews_per_day" in df_with_freq.columns
        # All frequencies should be >= 0
        assert df_with_freq.filter(col("reviews_per_day") < 0).count() == 0
    
    def test_rfm_score_ranges(self, spark):
        """Test that RFM scores are in expected ranges (0-10)."""
        data = [
            {"user_id": "u1", "recency_score": 8, "frequency_score": 9, "monetary_score": 7},
            {"user_id": "u2", "recency_score": 3, "frequency_score": 4, "monetary_score": 5}
        ]
        df = spark.createDataFrame(data)
        
        # Calculate RFM score
        df_with_rfm = df.withColumn(
            "rfm_score",
            (col("recency_score") + col("frequency_score") + col("monetary_score")) / 3
        )
        
        # All scores should be between 0 and 10
        invalid_scores = df_with_rfm.filter(
            (col("rfm_score") < 0) | (col("rfm_score") > 10)
        ).count()
        
        assert invalid_scores == 0
    
    def test_churn_risk_calculation(self, spark):
        """Test churn risk scoring logic."""
        data = [
            {"user_id": "u1", "days_since_last_review": 30},   # Low risk
            {"user_id": "u2", "days_since_last_review": 1000}, # Medium risk
            {"user_id": "u3", "days_since_last_review": 3000}  # High risk
        ]
        df = spark.createDataFrame(data)
        
        from pyspark.sql.functions import when
        
        df_with_risk = df.withColumn(
            "churn_risk",
            when(col("days_since_last_review") < 365, "low")
            .when(col("days_since_last_review") < 1825, "medium")
            .otherwise("high")
        )
        
        assert df_with_risk.filter(col("churn_risk") == "low").count() == 1
        assert df_with_risk.filter(col("churn_risk") == "medium").count() == 1
        assert df_with_risk.filter(col("churn_risk") == "high").count() == 1
    
    def test_no_negative_counts(self, spark, sample_business_data):
        """Test that all count features are non-negative."""
        df = spark.createDataFrame(sample_business_data)
        
        # Check review_count is non-negative
        negative_counts = df.filter(col("review_count") < 0).count()
        assert negative_counts == 0
    
    def test_feature_null_handling(self, spark):
        """Test that null features are handled (filled with 0)."""
        data = [
            {"user_id": "u1", "review_count": 10, "avg_stars": 4.5},
            {"user_id": "u2", "review_count": None, "avg_stars": None}
        ]
        df = spark.createDataFrame(data)
        
        # Fill nulls
        df_filled = df.fillna(0)
        
        assert df_filled.filter(col("review_count").isNull()).count() == 0
        assert df_filled.filter(col("avg_stars").isNull()).count() == 0
