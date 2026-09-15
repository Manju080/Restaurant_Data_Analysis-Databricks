# GitHub Actions Workflows

Automated CI/CD pipelines for the Yelp Churn Prediction project.

## Workflows

### 1. `databricks-ci.yml`
**Main CI/CD pipeline** - Runs on push to `main` or `develop` branches.

**Jobs:**
1. **test** - Run unit tests with pytest
2. **validate-notebooks** - Check notebook syntax and outputs
3. **deploy-dev** - Deploy to Dev workspace (on `develop` branch)
4. **deploy-prod** - Deploy to Production workspace (on `main` branch)

**Secrets Required:**
- `DATABRICKS_HOST` - Your Databricks workspace URL
- `DATABRICKS_TOKEN` - Personal access token

### 2. `test.yml`
**Lightweight test runner** - Runs on all pushes and PRs.

**Matrix:**
- Python versions: 3.9, 3.10, 3.11
- Runs pytest on all test files

### 3. `lint.yml`
**Code quality checks** - Runs on push to `main` or `develop`.

**Checks:**
- flake8 (PEP 8 compliance)
- black (code formatting)
- isort (import sorting)
- bandit (security vulnerabilities)

## Setup

### Add Secrets to GitHub
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `DATABRICKS_HOST`: `https://your-workspace.cloud.databricks.com`
   - `DATABRICKS_TOKEN`: Generate from Databricks User Settings → Access Tokens

### Enable Workflows
Workflows are automatically enabled when you push `.github/workflows/*.yml` files to GitHub.

### Manual Trigger
You can manually trigger the main workflow:
1. Go to **Actions** tab
2. Select **Databricks CI/CD Pipeline**
3. Click **Run workflow**

## Status Badges

Add these to your README.md:

```markdown
![CI/CD](https://github.com/your-username/your-repo/actions/workflows/databricks-ci.yml/badge.svg)
![Tests](https://github.com/your-username/your-repo/actions/workflows/test.yml/badge.svg)
![Lint](https://github.com/your-username/your-repo/actions/workflows/lint.yml/badge.svg)
```

## Environments

### Development (`develop` branch)
- Auto-deploy to `/Workspace/dev/yelp-churn-pipeline`
- No approval required

### Production (`main` branch)
- Auto-deploy to `/Workspace/prod/yelp-churn-pipeline`
- Requires manual approval (configure in GitHub Settings → Environments)

## Troubleshooting

### Authentication Failed
- Verify `DATABRICKS_HOST` and `DATABRICKS_TOKEN` secrets
- Check token hasn't expired

### Test Failures
- Run tests locally: `pytest tests/ -v`
- Check Python version compatibility

### Deployment Failures
- Verify workspace paths exist
- Check Databricks CLI configuration
