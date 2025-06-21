import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

# Create a sample dataset for training
# In a real project, this would come from a large, labeled dataset.
data = {
    'text': [
        'Invoice Number: INV-12345, Amount Due: $500.00, Vendor: Office Supplies Inc.',
        'This Service Agreement is made effective as of June 1, 2025, by and between Client Inc. and Service Provider LLC.',
        'Receipt for your purchase at The Corner Cafe. Total: $12.50. Paid with Visa.',
        'TAX INVOICE. Bill to: John Doe. Total Amount: 99.99',
        'This Non-Disclosure Agreement (the "Agreement") is entered into by and between a company and an individual.',
        'Cash Receipt. Item: Coffee, Price: 4.50. Thank you for your business.'
    ],
    'category': [
        'invoice',
        'contract',
        'receipt',
        'invoice',
        'contract',
        'receipt'
    ]
}
df = pd.DataFrame(data)

# Define the machine learning pipeline
# Step 1: Convert text to numerical vectors using TF-IDF
# Step 2: Train a Naive Bayes classifier
text_clf_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', MultinomialNB()),
])

# Train the model
print("Training the classification model...")
text_clf_pipeline.fit(df['text'], df['category'])
print("Training complete.")

# Define the path to save the models
model_dir = os.path.join(os.path.dirname(__file__), '..', 'ml_models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'document_classifier_pipeline.joblib')

# Save the entire trained pipeline to a file
joblib.dump(text_clf_pipeline, model_path)
print(f"Model saved successfully to {model_path}") 