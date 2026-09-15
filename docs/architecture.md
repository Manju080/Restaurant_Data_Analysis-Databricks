# 🏗️ System Architecture

## Overview

This project implements a **Medallion Architecture** (Bronze → Silver → Gold) for Yelp data processing and machine learning on Databricks.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│  (Yelp Academic Dataset - 5 JSON files, ~10 GB compressed)      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     🥉 BRONZE LAYER                              │
│  • Raw ingestion from DBFS/Volumes                               │
│  • Schema inference & enforcement                                │
│  • Minimal transformations                                       │
│  • Delta format for ACID compliance                              │
│                                                                   │
│  Tables:                                                          │
│    - yelp_dataset.bronze.yelp_business                           │
│    - yelp_dataset.bronze.yelp_review                             │
│    - yelp_dataset.bronze.yelp_user                               │
│    - yelp_dataset.bronze.yelp_checkin                            │
│    - yelp_dataset.bronze.yelp_tip                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     🥈 SILVER LAYER                              │
│  • Data quality validation                                       │
│  • Deduplication (review_id, user_id, business_id)              │
│  • Standardization (lowercase cities/states)                     │
│  • Type casting & null handling                                  │
│  • Business rules enforcement                                    │
│                                                                   │
│  Tables:                                                          │
│    - yelp_dataset.silver.yelp_business (64K businesses)         │
│    - yelp_dataset.silver.yelp_review (7M reviews)               │
│    - yelp_dataset.silver.yelp_user (480K users)                 │
│    - yelp_dataset.silver.yelp_checkin (132K records)            │
│    - yelp_dataset.silver.yelp_tip (909K tips)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     🥇 GOLD LAYER                                │
│  • Feature engineering (94 features)                             │
│  • Aggregations & business metrics                               │
│  • ML-ready datasets                                             │
│  • Advanced analytics tables                                     │
│                                                                   │
│  Tables:                                                          │
│    - business_features (64K rows, 67 columns)                   │
│    - user_features (480K rows, 45 columns)                      │
│    - review_features (7M rows, 35 columns)                      │
│    - time_series_features (monthly aggregations)                │
│    - cohort_analysis (retention metrics)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     🤖 ML LAYER                                  │
│  • XGBoost churn prediction model                                │
│  • 94 engineered features (RFM, polynomial, ratios)              │
│  • MLflow experiment tracking                                    │
│  • Batch predictions to Delta table                              │
│                                                                   │
│  Outputs:                                                         │
│    - churn_predictions (480K users scored)                      │
│    - Risk categories: Low/Medium/High/Critical                  │
│    - Model artifacts in MLflow Registry                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1️⃣ **Bronze Layer** (`01_bronze_yelp.ipynb`)
- **Input**: Raw JSON files from Yelp Academic Dataset
- **Processing**:
  - Read JSON with schema inference
  - Add metadata columns: `ingestion_timestamp`, `source_file`, `data_layer`
  - Write to Delta tables (append mode for incremental loads)
- **Output**: 5 Bronze Delta tables
- **Runtime**: ~5-10 minutes for full dataset

### 2️⃣ **Silver Layer** (`02_Silver_yelp.ipynb`)
- **Input**: Bronze Delta tables
- **Processing**:
  - **Business**: Parse attributes/hours JSON, create boolean flags (`is_restaurant`, `is_open`), normalize location fields
  - **Review**: Extract text features (length, word count), parse dates, cast types
  - **User**: Calculate tenure, parse elite years, flatten compliments
  - **Checkin**: Parse date arrays, count checkins per business
  - **Tip**: Basic cleaning and date parsing
  - Deduplicate on primary keys
  - Validation rules (star ratings 1-5, valid coordinates)
- **Output**: 5 Silver Delta tables (cleaned, validated)
- **Runtime**: ~15-20 minutes

### 3️⃣ **Gold Layer** (`03_Gold_layer.ipynb`)
- **Input**: Silver Delta tables
- **Processing**:
  - **Business Features**: Review aggregations, engagement scores, popularity metrics, rating consistency
  - **User Features**: RFM segmentation, churn risk scoring, user value calculation, activity patterns
  - **Review Features**: Sentiment proxies (exclamation/question counts, caps ratio), temporal features, deviation from business average
  - **Time Series**: Monthly review trends, growth rates, 3-month rolling averages
  - **Cohort Analysis**: User retention by cohort month
- **Output**: 5 Gold Delta tables (ML-ready)
- **Runtime**: ~30-40 minutes

### 4️⃣ **ML Layer** (`04_ML_Churn_Prediction.ipynb`)
- **Input**: `user_features` table
- **Processing**:
  - Define churn target: `days_since_last_review > median (3,018 days)`
  - Feature engineering:
    - Base features: 24 numeric columns
    - Log transformations: 16 features
    - Polynomial features: 10 features (degree 2)
    - Ratio features: 10 features (efficiency metrics)
    - Interaction features: 5 features (tenure × activity, engagement × value)
    - Domain features: 13 features (review velocity, consistency scores)
    - Binned features: 3 categorical bins
  - Train/test split: 80/20
  - Model: XGBoost Classifier
  - Hyperparameters: max_depth=6, learning_rate=0.1, n_estimators=100
  - MLflow tracking: Params, metrics, model artifacts
  - Batch scoring: All 480K users
- **Output**: `churn_predictions` table with risk categories
- **Runtime**: ~20-30 minutes (480K users)

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|----------|
| **Compute** | Databricks Serverless | Auto-scaling, no cluster management |
| **Storage** | Delta Lake | ACID transactions, time travel, versioning |
| **Catalog** | Unity Catalog | Centralized governance, lineage, permissions |
| **Processing** | Apache Spark (PySpark) | Distributed data processing |
| **ML** | XGBoost + scikit-learn | Gradient boosting, feature engineering |
| **Tracking** | MLflow | Experiment tracking, model registry |
| **Language** | Python 3.10 | Primary development language |

---

## Data Quality Checks

### Bronze → Silver
- ✅ Deduplicate on primary keys
- ✅ Validate star ratings (1-5 range)
- ✅ Validate coordinates (lat: -90 to 90, lon: -180 to 180)
- ✅ Cast types (strings to dates, integers)
- ✅ Handle nulls (fill or filter)

### Silver → Gold
- ✅ Ensure no negative counts
- ✅ Validate aggregation logic (avg, sum, count)
- ✅ Check for missing join keys
- ✅ Verify feature distributions (no extreme outliers)

### Gold → ML
- ✅ Check for missing features (fillna with 0)
- ✅ Remove infinite values
- ✅ Verify class balance (50/50 churn split)
- ✅ Feature scaling (StandardScaler)

---

## Scalability Considerations

### Current Scale
- **Data**: ~10 GB compressed, ~50 GB uncompressed
- **Rows**: 8.6M total (7M reviews + 480K users + 65K businesses)
- **Compute**: Databricks Serverless (auto-scales 1-32 nodes)

### Future Scale (10x growth)
- **Data**: 100 GB → Use Spark partitioning by date/location
- **Rows**: 86M → Incremental processing (process only new data)
- **Strategy**:
  - Partition Bronze tables by `ingestion_date`
  - Use Delta Lake merge for incremental Silver updates
  - Aggregate only new data in Gold layer
  - Retrain model monthly instead of full refresh

---

## Security & Governance

### Unity Catalog Setup
```sql
-- Catalog structure
yelp_dataset/
  ├── bronze/    (READ: data_engineers, WRITE: etl_service_principal)
  ├── silver/    (READ: data_analysts, WRITE: data_engineers)
  └── gold/      (READ: all_users, WRITE: data_engineers)
```

### Access Control
- **Bronze**: Restricted to ETL pipelines
- **Silver**: Analysts can read for exploration
- **Gold**: Public read access (ML-ready data)
- **Churn Predictions**: Restricted to business stakeholders

---

## Monitoring & Observability

### Metrics to Track
1. **Data Quality**: Null counts, duplicate counts, validation failures
2. **Performance**: Job runtime, shuffle spills, data skew
3. **Model**: ROC-AUC, precision, recall, prediction drift
4. **Business**: High-risk user count, churn rate trends

### Alerting
- ⚠️ Bronze ingestion failures
- ⚠️ Silver validation errors > 5%
- ⚠️ Gold feature nulls > 1%
- ⚠️ Model ROC-AUC drop > 0.05

---

## Future Enhancements

### Short Term (1-3 months)
- [ ] Add streaming layer for real-time review ingestion
- [ ] Implement data quality dashboard (Lakeview)
- [ ] Create CI/CD pipeline for automated testing
- [ ] Add more ML models (classification, clustering)

### Long Term (6-12 months)
- [ ] Real-time churn scoring API (Model Serving)
- [ ] A/B testing framework for retention campaigns
- [ ] Advanced NLP on review text (sentiment, topics)
- [ ] Graph analysis (user-business network)

---

## References

- [Medallion Architecture Best Practices](https://www.databricks.com/glossary/medallion-architecture)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Unity Catalog Guide](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)