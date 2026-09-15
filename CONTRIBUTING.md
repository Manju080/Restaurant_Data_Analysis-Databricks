# Contributing to Yelp Churn Prediction

Thank you for your interest in contributing! This project is primarily a portfolio/educational project, but contributions are welcome.

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/your-feature`)
3. **Make your changes**
4. **Test locally** on Databricks Community Edition or your workspace
5. **Commit** with clear messages (`git commit -m 'Add feature: ...'`)
6. **Push** to your fork (`git push origin feature/your-feature`)
7. **Open a Pull Request**

## Development Setup

1. Clone the repo to your Databricks workspace (via Repos)
2. Upload Yelp dataset to `/Volumes/yelp_dataset/default/raw_yelp`
3. Run notebooks in order: Bronze → Silver → Gold → ML

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions/classes
- Keep notebook cells focused (one concept per cell)

## Testing

- Test notebooks cell-by-cell before committing
- Ensure Delta tables are created successfully
- Verify MLflow experiment tracking works

## Questions?

Open an issue or reach out via email.
