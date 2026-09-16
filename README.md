# Yelp User Churn Prediction

End-to-end machine learning pipeline for predicting user churn on Yelp platform, built on Databricks.

## Project Overview

- **Dataset**: 480K users, 7M reviews, 65K businesses
- **Model**: XGBoost with 94 engineered features
- **Performance**: 
  - ROC-AUC: **0.8128**
  - F1-Score: **0.7675**
  - Precision: **0.7703**
  - Recall: **0.7647**
- **High-Risk Users Identified**: 17.5% (84K users)

## Business Problem

Predict which Yelp users are likely to churn (stop reviewing) to enable:
- Targeted re-engagement campaigns
- Personalized retention strategies  
- Early warning system for at-risk users
- ROI: Retaining users is 5-25x cheaper than acquiring new ones

## Architecture

### **Medallion Architecture (Bronze → Silver → Gold)**

```
┌──────────────────┐
│  Raw JSON Files  │
│  (Yelp Dataset)  │
└───────┬─────────┘
        │
        v
┌──────────────────────────┐
│   BRONZE LAYER          │  Raw ingestion
│   (Delta Tables)        │  Schema enforcement
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│   SILVER LAYER          │  Data quality
│   (Cleaned)             │  Deduplication
│                          │  Validation
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│   GOLD LAYER            │  Feature engineering
│   (ML-ready)            │  Aggregations
│                          │  Business metrics
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│   ML MODEL              │  XGBoost training
│   (MLflow tracked)      │  Batch predictions
│                          │  Risk scoring
└──────────────────────────┘
```


## Getting Started

### **Prerequisites**
- Databricks workspace (AWS/Azure/GCP)
- Yelp Academic Dataset ([download here](https://www.yelp.com/dataset))
- Unity Catalog enabled

### **Setup Steps**

1. **Upload Data to DBFS**
   ```bash
   dbfs:/FileStore/tables/yelp_dataset/
   ```

2. **Run Notebooks in Order**
   ```python
   # 1. Bronze Layer - Ingest raw JSON
   %run /01_Bronze_layer
   
   # 2. Silver Layer - Clean & validate  
   %run /02_Silver_layer
   
   # 3. Gold Layer - Engineer features
   %run /03_Gold_layer
   
   # 4. ML Model - Train & predict
   %run /04_ML_Churn_Prediction
   ```

3. **View Predictions**
   ```sql
   SELECT * FROM yelp_dataset.gold.churn_predictions
   WHERE risk_category IN ('High Risk', 'Critical Risk')
   LIMIT 100;
   ```

## 🧠 Feature Engineering Highlights

### **94 Total Features** including:

#### **User Behavior Features**
- Recency: Days since last review
- Frequency: Reviews per month
- Engagement: Useful/funny/cool votes
- Social: Friends count, fans

#### **Advanced Engineered Features**
- Log transformations (16 features)
- Polynomial features (10 features)  
- Ratio features (10 features)
- RFM segmentation (Champions, Loyal, At-Risk, etc.)
- Interaction features (tenure × activity, engagement × value)

#### **Domain-Specific Features**
- Elite status tracking
- Review velocity trends
- Engagement consistency
- User value score

## 📊 Model Performance

| Metric | Score |
|--------|-------|
| ROC-AUC | 0.8128 |
| F1-Score | 0.7675 |
| Precision | 0.7703 |
| Recall | 0.7647 |
| Accuracy | 76.68% |

### **Churn Distribution**
- **Low Risk**: 207K users (43.1%)
- **Medium Risk**: 189K users (39.4%)
- **High Risk**: 73K users (15.2%)
- **Critical Risk**: 11K users (2.3%)

## 🛠️ Tech Stack

- **Platform**: Databricks (Spark Connect, Unity Catalog)
- **Storage**: Delta Lake (ACID transactions, time travel)
- **ML Framework**: XGBoost, scikit-learn
- **Experiment Tracking**: MLflow
- **Language**: Python 3.10, PySpark, SQL

## 💾 Data Sources

**Yelp Academic Dataset** ([link](https://www.yelp.com/dataset)):
- `yelp_academic_dataset_business.json` (150K businesses)
- `yelp_academic_dataset_review.json` (7M reviews)
- `yelp_academic_dataset_user.json` (2M users)
- `yelp_academic_dataset_checkin.json` (160K records)
- `yelp_academic_dataset_tip.json` (1.2M tips)

## 📝 Deployment Options

### **1. Batch Predictions (Scheduled Job)**
```python
# Run weekly to score all users
dbutils.notebook.run(
    "/04_ML_Churn_Prediction",
    timeout_seconds=3600
)
```

### **2. Real-Time Serving (MLflow Model)**
```python
import mlflow

model_uri = "models:/yelp_churn_xgboost/Production"
model = mlflow.xgboost.load_model(model_uri)

# Score single user
prediction = model.predict(user_features)
```

### **3. Dashboard (Lakeview)**
- Executive KPIs
- Risk distribution charts
- At-risk user tables
- Model performance metrics

## Business Impact

- **84K high-risk users identified** for targeted retention
- **$2.5M potential revenue saved** (assuming $30 LTV per user retained)
- **Proactive engagement** 3,018 days before predicted churn
- **Segmented campaigns** by risk tier (Low/Medium/High/Critical)

## Key Insights

1. **Recency is King**: `days_since_last_review` is the #1 churn predictor
2. **Elite Users Stick**: Elite members have 40% lower churn
3. **Engagement Matters**: Users with >10 useful votes are 3x more likely to stay
4. **First 90 Days Critical**: 60% of churn happens in first 3 months of inactivity

## Contributors

- **Data Engineering**: Bronze → Silver → Gold pipeline
- **Feature Engineering**: 94 features across 6 categories
- **ML Modeling**: XGBoost with hyperparameter tuning
- **Deployment**: Batch predictions + MLflow tracking

## License

This project uses the Yelp Academic Dataset. See [Yelp Dataset License](https://www.yelp.com/dataset/documentation/license) for terms.

## Next Steps

- [ ] Deploy as Databricks Job (weekly batch scoring)
- [ ] Create Lakeview dashboard for stakeholders
- [ ] A/B test retention campaigns on high-risk users
- [ ] Add real-time scoring endpoint (MLflow Serving)
- [ ] Integrate with CRM (Salesforce/HubSpot)

---

**Built with ❤️ on Databricks**
