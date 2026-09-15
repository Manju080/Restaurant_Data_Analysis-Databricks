# Test Suite

Unit tests for Yelp Churn Prediction pipeline.

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_bronze_layer.py
pytest tests/test_silver_layer.py
pytest tests/test_gold_layer.py
pytest tests/test_ml_churn.py
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

## Test Structure

* `conftest.py` - Pytest configuration and shared fixtures
* `test_bronze_layer.py` - Tests for raw data ingestion
* `test_silver_layer.py` - Tests for data cleaning and validation
* `test_gold_layer.py` - Tests for feature engineering
* `test_ml_churn.py` - Tests for ML model training and prediction

## Requirements

```bash
pip install pytest pytest-cov
```

## Coverage Goals

* Bronze Layer: 90%+
* Silver Layer: 90%+
* Gold Layer: 85%+
* ML Layer: 80%+
