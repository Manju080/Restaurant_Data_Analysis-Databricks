# 🚀 Deployment Guide

Complete guide to deploying the Yelp Churn Prediction pipeline on Databricks.

---

## Prerequisites

### 1️⃣ **Databricks Workspace**
- **Account**: Databricks AWS, Azure, or GCP
- **Tier**: Standard or Premium (for Unity Catalog)
- **Compute**: Serverless enabled (or provisioned cluster with DBR 13.3+)

### 2️⃣ **Data Access**
- Download [Yelp Academic Dataset](https://www.yelp.com/dataset)
- **Size**: ~10 GB compressed (5 JSON files)
- **Files**: `yelp_academic_dataset_business.json`, `review.json`, `user.json`, `checkin.json`, `tip.json`

### 3️⃣ **Permissions**
- Workspace Admin (for catalog creation)
- Cluster create/attach permissions
- Unity Catalog CREATE SCHEMA/TABLE permissions

---

## 📚 Step-by-Step Deployment

### **Step 1: Upload Data to Databricks**

#### Option A: DBFS (Quick Start)
```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# Upload dataset
databricks fs cp yelp_academic_dataset_business.json dbfs:/FileStore/yelp_data/
databricks fs cp yelp_academic_dataset_review.json dbfs:/FileStore/yelp_data/
databricks fs cp yelp_academic_dataset_user.json dbfs:/FileStore/yelp_data/
databricks fs cp yelp_academic_dataset_checkin.json dbfs:/FileStore/yelp_data/
databricks fs cp yelp_academic_dataset_tip.json dbfs:/FileStore/yelp_data/
```

#### Option B: Unity Catalog Volumes (Recommended)
```sql
-- In Databricks SQL or notebook
CREATE CATALOG IF NOT EXISTS yelp_dataset;
USE CATALOG yelp_dataset;

CREATE SCHEMA IF NOT EXISTS default;

CREATE VOLUME IF NOT EXISTS yelp_dataset.default.raw_yelp;
```

Then upload via UI:
1. Navigate to **Catalog** → `yelp_dataset` → `default` → `raw_yelp`
2. Click **Upload Files**
3. Select all 5 JSON files

---

### **Step 2: Create Unity Catalog Structure**

Run this SQL in a notebook or SQL editor:

```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS yelp_dataset
  COMMENT 'Yelp user churn prediction project';

-- Create schemas
CREATE SCHEMA IF NOT EXISTS yelp_dataset.bronze
  COMMENT 'Raw data ingestion layer';

CREATE SCHEMA IF NOT EXISTS yelp_dataset.silver
  COMMENT 'Cleaned and validated data';

CREATE SCHEMA IF NOT EXISTS yelp_dataset.gold
  COMMENT 'ML-ready feature tables';

-- Verify
SHOW SCHEMAS IN yelp_dataset;
```

**Expected Output:**
```
| schema_name | comment                         |
|-------------|---------------------------------|
| bronze      | Raw data ingestion layer        |
| default     | Default schema                  |
| gold        | ML-ready feature tables         |
| silver      | Cleaned and validated data      |
```

---

### **Step 3: Update Data Paths in Notebooks**

#### If using DBFS:
In `01_bronze_yelp.ipynb`, update paths:
```python
self.raw_data_path = "dbfs:/FileStore/yelp_data/"
```

#### If using Unity Catalog Volumes:
```python
self.raw_data_path = "/Volumes/yelp_dataset/default/raw_yelp/"
```

---

### **Step 4: Run Notebooks in Order**

#### 1️⃣ **Bronze Layer**
```python
# Open: 01_bronze_yelp.ipynb
# Click: Run All
# Expected runtime: 5-10 minutes
```

**Validation:**
```sql
SELECT 'business' AS table_name, COUNT(*) AS row_count 
FROM yelp_dataset.bronze.yelp_business
UNION ALL
SELECT 'review', COUNT(*) FROM yelp_dataset.bronze.yelp_review
UNION ALL
SELECT 'user', COUNT(*) FROM yelp_dataset.bronze.yelp_user
UNION ALL
SELECT 'checkin', COUNT(*) FROM yelp_dataset.bronze.yelp_checkin
UNION ALL
SELECT 'tip', COUNT(*) FROM yelp_dataset.bronze.yelp_tip;
```

**Expected Counts:**
- business: ~65,000
- review: ~7,000,000
- user: ~480,000
- checkin: ~132,000
- tip: ~909,000

#### 2️⃣ **Silver Layer**
```python
# Open: 02_Silver_yelp.ipynb
# Click: Run All
# Expected runtime: 15-20 minutes
```

**Validation:**
```sql
-- Check for duplicates (should be 0)
SELECT COUNT(*) - COUNT(DISTINCT business_id) AS duplicates
FROM yelp_dataset.silver.yelp_business;

-- Check star rating validity
SELECT MIN(stars), MAX(stars)
FROM yelp_dataset.silver.yelp_review;
-- Expected: 1, 5
```

#### 3️⃣ **Gold Layer**
```python
# Open: 03_Gold_layer.ipynb
# Click: Run All
# Expected runtime: 30-40 minutes
```

**Validation:**
```sql
-- Check feature table
SELECT 
  COUNT(*) AS total_users,
  AVG(user_total_reviews) AS avg_reviews,
  COUNT(DISTINCT user_segment) AS segments
FROM yelp_dataset.gold.user_features;

-- Expected:
-- total_users: 480,189
-- avg_reviews: ~146
-- segments: 10
```

#### 4️⃣ **ML Layer**
```python
# Open: 04_ML_Churn_Prediction.ipynb
# Click: Run All
# Expected runtime: 20-30 minutes
```

**Validation:**
```python
# Check predictions
predictions_df = spark.table("yelp_dataset.gold.churn_predictions")

predictions_df.groupBy("risk_category").count().orderBy("risk_category").show()

# Expected distribution:
# Low Risk: ~60%
# Medium Risk: ~20%
# High Risk: ~15%
# Critical Risk: ~5%
```

---

### **Step 5: Verify MLflow Experiments**

1. Go to **Machine Learning** → **Experiments**
2. Find experiment: `/Users/<your_email>/yelp_churn_prediction`
3. Verify metrics:
   - ROC-AUC: ~0.81
   - Precision: ~0.77
   - Recall: ~0.76
   - F1-Score: ~0.77

---

## ⚙️ Configuration Options

### Cluster Configuration

#### Option 1: Serverless (Recommended)
- **Pros**: No setup, auto-scaling, cost-effective
- **Cons**: Cold start (30-60 seconds)
- **Use for**: Production pipelines, scheduled jobs

#### Option 2: Provisioned Cluster
```json
{
  "cluster_name": "yelp-churn-pipeline",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 2,
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  },
  "spark_conf": {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true"
  }
}
```

**Use for**: Interactive development, debugging

---

## 📦 Scheduling (Optional)

### Create a Lakeflow Job

1. Go to **Workflows** → **Create Job**
2. Add tasks:

**Task 1: Bronze Ingestion**
- Type: Notebook
- Path: `01_bronze_yelp.ipynb`
- Cluster: Serverless

**Task 2: Silver Cleaning** (depends on Task 1)
- Type: Notebook
- Path: `02_Silver_yelp.ipynb`
- Cluster: Serverless

**Task 3: Gold Features** (depends on Task 2)
- Type: Notebook
- Path: `03_Gold_layer.ipynb`
- Cluster: Serverless

**Task 4: ML Scoring** (depends on Task 3)
- Type: Notebook
- Path: `04_ML_Churn_Prediction.ipynb`
- Cluster: Serverless

3. **Schedule**: Daily at 2 AM UTC
4. **Alerts**: Email on failure

---

## 🐛 Troubleshooting

### Issue: "Catalog not found"
**Solution:**
```sql
CREATE CATALOG IF NOT EXISTS yelp_dataset;
USE CATALOG yelp_dataset;
```

### Issue: "File not found" in Bronze layer
**Solution:**
- Verify file paths:
  ```python
  dbutils.fs.ls("/Volumes/yelp_dataset/default/raw_yelp/")
  ```
- Check file names match exactly (case-sensitive)

### Issue: "Memory error" during Gold layer
**Solution:**
- Increase cluster size (or let Serverless auto-scale)
- Add repartitioning:
  ```python
  df = df.repartition(200)  # Increase parallelism
  ```

### Issue: "Model ROC-AUC < 0.70"
**Solution:**
- Check class balance:
  ```python
  train_df.groupBy("is_churned").count().show()
  ```
- Verify feature engineering:
  ```python
  feature_df.describe().show()
  ```

### Issue: "Predictions table empty"
**Solution:**
- Verify model logged to MLflow
- Check batch scoring cell ran successfully
- Verify write permissions on `gold` schema

---

## 🔒 Security Checklist

- [x] Unity Catalog enabled
- [x] Access controls on schemas (GRANT/REVOKE)
- [x] Data at rest encrypted (Delta Lake)
- [x] Secrets stored in Databricks Secret Scopes (not hardcoded)
- [x] Audit logs enabled (system tables)
- [x] Network isolation (VPC/VNet if required)

---

## 📊 Monitoring

### Data Quality Metrics
```sql
-- Daily monitoring query
SELECT 
  CURRENT_DATE() AS check_date,
  COUNT(*) AS total_records,
  COUNT(DISTINCT user_id) AS unique_users,
  SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) / COUNT(*) AS churn_rate,
  AVG(churn_probability) AS avg_churn_prob
FROM yelp_dataset.gold.churn_predictions
WHERE prediction_date = CURRENT_DATE();
```

### Alert Thresholds
- 🟢 **Healthy**: Churn rate 45-55%, avg_prob 0.45-0.55
- 🟡 **Warning**: Churn rate 40-45% or 55-60%
- 🔴 **Critical**: Churn rate < 40% or > 60% (data drift!)

---

## 🌐 Deployment Environments

### Development
- **Workspace**: `dev-workspace`
- **Catalog**: `yelp_dataset_dev`
- **Cluster**: Single-node (for testing)
- **Data**: Sample (10K users)

### Staging
- **Workspace**: `staging-workspace`
- **Catalog**: `yelp_dataset_staging`
- **Cluster**: Serverless (2-4 nodes)
- **Data**: Full dataset (480K users)
- **Purpose**: Pre-prod validation

### Production
- **Workspace**: `prod-workspace`
- **Catalog**: `yelp_dataset`
- **Cluster**: Serverless (auto-scale 2-32)
- **Data**: Full dataset + incremental updates
- **Monitoring**: 24/7 alerts

---

## 📝 Post-Deployment Checklist

- [ ] All 5 Bronze tables created
- [ ] All 5 Silver tables created
- [ ] All 5 Gold tables created
- [ ] Churn predictions table exists
- [ ] MLflow experiment logged
- [ ] Model ROC-AUC > 0.70
- [ ] Job scheduled (if applicable)
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] Team trained on pipeline

---

## 🚀 Next Steps

1. **Dashboard**: Create Lakeview dashboard for churn insights
2. **API**: Deploy model to Model Serving endpoint
3. **Alerts**: Set up email/Slack alerts for high-risk users
4. **Retrain**: Schedule monthly model retraining
5. **A/B Test**: Implement retention campaigns for high-risk cohorts

---

## Support

- **Databricks Docs**: [docs.databricks.com](https://docs.databricks.com)
- **Community**: [community.databricks.com](https://community.databricks.com)
- **Issues**: Open a GitHub issue on this repo

---

**✅ Deployment Complete! Your churn prediction pipeline is live.**