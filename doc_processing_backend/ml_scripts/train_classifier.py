import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
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
        'Invoice #A12345 for professional services rendered. Payment due within 30 days.',
        'Final Notice: Invoice #789-XYZ overdue. Please remit payment of $1,200.00 immediately.',
        'Monthly subscription invoice. Period: Jan 1-31, 2023. Amount: $29.99 plus applicable taxes.',
        
        # Receipts
        'Receipt for your purchase at The Corner Cafe. Total: $12.50. Paid with Visa.',
        'Cash Receipt. Item: Coffee, Price: 4.50. Thank you for your business.',
        'Digital Receipt - Amazon.com - Order #123-4567890-1234567 - Total: $67.89',
        'Store: Walmart Superstore - Register: 12 - Cashier: Mike - Items: 15 - Total: $123.45',
        'Parking Receipt - Duration: 2hrs - Fee: $8.00 - Thank you for parking with us!',
        
        # Journals
        'The study found a significant correlation (p < 0.05) between variables. These findings are discussed in the context of existing literature.',
        'Journal of Neuroscience, Volume 44, Issue 2. Abstract: We investigate the neural pathways...',
        'A systematic review of 42 studies revealed that intervention X led to a mean reduction of 15% in symptoms.',
        'This paper proposes a novel algorithm for image recognition that outperforms existing methods by 12% on benchmark datasets.',
        'In this longitudinal study spanning 10 years, we observed significant trends in climate patterns affecting local ecosystems.',
        
        # Advertisements
        'Limited time offer! Get 50% off all summer clothing. Shop now and save big!',
        'Introducing the new hydro-car. Unbelievable mileage. Visit our showroom today.',
        'Flash Sale! This weekend only. Use code SAVE20 for an extra 20% off already reduced prices.',
        'New iPhone 15 Pro - The most advanced smartphone ever. Pre-order today and get free AirPods.',
        'Hungry? Order online now and get free delivery on orders over $25. Download our app today!',
        
        # Emails
        'Hi Team, Just a reminder about the meeting scheduled for 3 PM tomorrow. Please find the agenda attached. Best, Jane Doe',
        'Subject: Your Order Confirmation. Thank you for your recent order. Your items are being prepared for shipment.',
        'Dear valued customer, We\'re writing to inform you about changes to our privacy policy effective June 1st.',
        'RE: Project Timeline Update - Please review the attached Gantt chart with the revised deadlines.',
        'Hello! I hope this email finds you well. I wanted to follow up on our conversation from last week about the marketing strategy.',
        
        # Forms
        'Please fill out all required fields. First Name: ____ Last Name: ____ Date of Birth: ____',
        'Application Form. Section A: Personal Details. Section B: Educational Background.',
        'Medical History Form - Patient ID: _____ - Allergies: _____ - Current Medications: _____',
        'Employee Feedback Survey: On a scale of 1-5, how would you rate your job satisfaction? _____',
        'Travel Expense Claim Form - Employee Name: _____ - Department: _____ - Trip Purpose: _____',
        
        # Letters
        'Dear Mr. Smith, I am writing to express my interest in the Software Engineer position advertised on your website.',
        'To whom it may concern, this letter is to certify that...',
        'Dear Homeowner, We are writing to inform you about the upcoming neighborhood association meeting scheduled for July 15th.',
        'Letter of Recommendation: It is with great pleasure that I recommend Ms. Jane Smith for the position of Marketing Director.',
        'Formal Notice: Please be advised that your tenancy agreement will expire on December 31st, 2023.',
        
        # Resumes
        'John Doe - Highly motivated Software Engineer with 5 years of experience in Python and cloud computing. Skills: Python, AWS, SQL.',
        'Curriculum Vitae: Jane Smith. Education: M.S. in Computer Science. Experience: Senior Developer at Tech Corp.',
        'Professional Resume - Marketing Specialist with 7+ years experience in digital marketing campaigns and social media management.',
        'ROBERT JOHNSON - Engineering Professional - 10+ years in automotive design - Patents: 3 - Publications: 12',
        'Executive Resume: Sarah Williams, MBA - Chief Operations Officer with proven track record of organizational transformation and revenue growth.'
    ],
    'category': [
        'invoice', 'invoice', 'invoice', 'invoice', 'invoice',
        'receipt', 'receipt', 'receipt', 'receipt', 'receipt',
        'journal', 'journal', 'journal', 'journal', 'journal',
        'advertisement', 'advertisement', 'advertisement', 'advertisement', 'advertisement',
        'email', 'email', 'email', 'email', 'email',
        'form', 'form', 'form', 'form', 'form',
        'letter', 'letter', 'letter', 'letter', 'letter',
        'resume', 'resume', 'resume', 'resume', 'resume'
    ]
}
df = pd.DataFrame(data)

# Define the machine learning pipeline
# Step 1: Convert text to numerical vectors using TF-IDF with improved parameters
# Step 2: Train a LinearSVC classifier which often performs better for text classification
text_clf_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.85)),
    ('clf', LinearSVC(C=1.0, class_weight='balanced')),
])

# Alternatively, uncomment these lines to use MLPClassifier (Neural Network) instead
# text_clf_pipeline = Pipeline([
#     ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.85)),
#     ('clf', MLPClassifier(hidden_layer_sizes=(100,), max_iter=300, activation='relu', 
#                         solver='adam', early_stopping=True, random_state=42)),
# ])

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