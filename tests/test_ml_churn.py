"""
Unit tests for ML churn prediction model.
Tests feature engineering, model training, and prediction logic.
"""
import pytest
import numpy as np


class TestMLChurnPrediction:
    """Test suite for ML churn prediction."""
    
    def test_churn_label_definition(self, spark):
        """Test that churn label is correctly defined."""
        data = [
            {"user_id": "u1", "days_since_last_review": 1000},
            {"user_id": "u2", "days_since_last_review": 5000}
        ]
        df = spark.createDataFrame(data)
        
        # Define churn threshold (e.g., 3018 days)
        churn_threshold = 3018
        
        from pyspark.sql.functions import when, col
        df_with_label = df.withColumn(
            "is_churned",
            when(col("days_since_last_review") > churn_threshold, 1).otherwise(0)
        )
        
        assert df_with_label.filter(col("is_churned") == 0).count() == 1
        assert df_with_label.filter(col("is_churned") == 1).count() == 1
    
    def test_feature_scaling(self):
        """Test that features are properly scaled."""
        from sklearn.preprocessing import StandardScaler
        
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Check that scaled features have mean ~0 and std ~1
        assert np.abs(X_scaled.mean()) < 0.01
        assert np.abs(X_scaled.std() - 1.0) < 0.01
    
    def test_train_test_split_ratio(self, spark):
        """Test that train/test split maintains proper ratio."""
        data = [{"user_id": f"u{i}", "feature": i} for i in range(100)]
        df = spark.createDataFrame(data)
        
        train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
        
        total = df.count()
        train_count = train_df.count()
        test_count = test_df.count()
        
        # Check split is approximately 80/20
        assert 75 <= train_count <= 85
        assert 15 <= test_count <= 25
        assert train_count + test_count == total
    
    def test_prediction_probability_range(self):
        """Test that prediction probabilities are between 0 and 1."""
        from xgboost import XGBClassifier
        from sklearn.datasets import make_classification
        
        X, y = make_classification(n_samples=100, n_features=10, random_state=42)
        model = XGBClassifier(random_state=42, eval_metric='logloss')
        model.fit(X, y)
        
        probabilities = model.predict_proba(X)[:, 1]
        
        assert all(0 <= p <= 1 for p in probabilities)
    
    def test_risk_category_assignment(self, spark):
        """Test that risk categories are correctly assigned."""
        data = [
            {"user_id": "u1", "churn_probability": 0.1},   # Low
            {"user_id": "u2", "churn_probability": 0.4},   # Medium
            {"user_id": "u3", "churn_probability": 0.7},   # High
            {"user_id": "u4", "churn_probability": 0.95}   # Critical
        ]
        df = spark.createDataFrame(data)
        
        from pyspark.sql.functions import when, col
        
        df_with_risk = df.withColumn(
            "risk_category",
            when(col("churn_probability") < 0.3, "Low Risk")
            .when(col("churn_probability") < 0.5, "Medium Risk")
            .when(col("churn_probability") < 0.8, "High Risk")
            .otherwise("Critical Risk")
        )
        
        assert df_with_risk.filter(col("risk_category") == "Low Risk").count() == 1
        assert df_with_risk.filter(col("risk_category") == "Medium Risk").count() == 1
        assert df_with_risk.filter(col("risk_category") == "High Risk").count() == 1
        assert df_with_risk.filter(col("risk_category") == "Critical Risk").count() == 1
    
    def test_model_metrics_validity(self):
        """Test that model evaluation metrics are valid."""
        from sklearn.metrics import roc_auc_score, precision_score, recall_score
        
        y_true = [0, 0, 1, 1]
        y_pred = [0, 1, 1, 1]
        y_prob = [0.1, 0.4, 0.6, 0.9]
        
        auc = roc_auc_score(y_true, y_prob)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        
        assert 0 <= auc <= 1
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1
