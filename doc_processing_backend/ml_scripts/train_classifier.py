import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

# Create an expanded sample dataset for training.
# In a real-world project, this dataset would be much larger for higher accuracy.
data = {
    'text': [
        # Invoices
        'Invoice Number: INV-123, Amount Due: $500.00, Vendor: Office Supplies Inc.',
        'TAX INVOICE. Bill to: John Doe. Total Amount: 99.99',
        # Receipts
        'Receipt for your purchase at The Corner Cafe. Total: $12.50. Paid with Visa.',
        'Cash Receipt. Item: Coffee, Price: 4.50. Thank you for your business.',
        # Journals
        'The study found a significant correlation (p < 0.05) between variables. These findings are discussed in the context of existing literature.',
        'Journal of Neuroscience, Volume 44, Issue 2. Abstract: We investigate the neural pathways...',
        # Advertisements
        'Limited time offer! Get 50% off all summer clothing. Shop now and save big!',
        'Introducing the new hydro-car. Unbelievable mileage. Visit our showroom today.',
        # Emails
        'Hi Team, Just a reminder about the meeting scheduled for 3 PM tomorrow. Please find the agenda attached. Best, Jane Doe',
        'Subject: Your Order Confirmation. Thank you for your recent order. Your items are being prepared for shipment.',
        # Forms
        'Please fill out all required fields. First Name: ____ Last Name: ____ Date of Birth: ____',
        'Application Form. Section A: Personal Details. Section B: Educational Background.',
        # Letters
        'Dear Mr. Smith, I am writing to express my interest in the Software Engineer position advertised on your website.',
        'To whom it may concern, this letter is to certify that...',
        # Resumes
        'John Doe - Highly motivated Software Engineer with 5 years of experience in Python and cloud computing. Skills: Python, AWS, SQL.',
        'Curriculum Vitae: Jane Smith. Education: M.S. in Computer Science. Experience: Senior Developer at Tech Corp.'
    ],
    'category': [
        'invoice', 'invoice',
        'receipt', 'receipt',
        'journal', 'journal',
        'advertisement', 'advertisement',
        'email', 'email',
        'form', 'form',
        'letter', 'letter',
        'resume', 'resume'
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

# Train the model on the new, larger dataset
print("Training the expanded classification model...")
text_clf_pipeline.fit(df['text'], df['category'])
print("Training complete.")

# Define the path to save the models
model_dir = os.path.join(os.path.dirname(__file__), '..', 'ml_models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'document_classifier_pipeline.joblib')

# Save the entire trained pipeline to a file
joblib.dump(text_clf_pipeline, model_path)
print(f"Model saved successfully to {model_path}") 