# Model Architecture & Learning Dynamics

## 1. Overview
This document outlines how the sentiment classification model learns from data, detailing the algorithm, objective functions, optimization mechanics, and learning progression.

## 2. Learning Mechanism
Depending on the chosen baseline or advanced model:

### A. Classical Machine Learning (e.g., Logistic Regression / Linear SVM / Naive Bayes)
- **Feature Space**: High-dimensional sparse TF-IDF vectors (n-grams).
- **Objective Function**: Cross-Entropy / Log Loss (Logistic) or Hinge Loss (SVM).
- **Optimization**: L-BFGS, SGD, or Coordinate Descent with L1/L2 regularization to prevent overfitting on vocabulary noise.

### B. Deep Learning / Transformer Approach (e.g., DistilBERT / BiLSTM)
- **Feature Space**: Dense contextual token embeddings (768-d).
- **Objective Function**: Categorical / Binary Cross-Entropy Loss.
- **Optimization**: AdamW optimizer with weight decay and warmup learning rate schedules.
- **Backpropagation**: Gradients calculated via reverse-mode autodiff, updating weights layer-by-layer.

## 3. Evaluation & Validation Metrics
- **Accuracy**: Overall correct prediction ratio.
- **Precision, Recall, F1-Score**: Weighted and macro-averaged (vital for imbalanced sentiment datasets).
- **ROC-AUC & PR-AUC**: For probabilistic threshold calibration.
- **Confusion Matrix**: Error diagnosis across true positive, false positive, true negative, false negative sentiment bins.
