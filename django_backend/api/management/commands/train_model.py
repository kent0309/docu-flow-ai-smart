from django.core.management.base import BaseCommand
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import torch

# Define a simple PyTorch Dataset
class DocDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

class Command(BaseCommand):
    help = 'Fine-tunes a document classification model'

    def handle(self, *args, **options):
        self.stdout.write("Starting model training...")

        # --- 1. Load Data ---
        # IMPORTANT: This is placeholder data. In a real application,
        # you would load and label your documents from the `media/training_data` folder.
        texts = [
            "Invoice for services rendered.", "This is a contract agreement.",
            "Receipt for your purchase.", "Another invoice for product X."
        ]
        labels = [0, 1, 2, 0] # 0: invoice, 1: contract, 2: receipt
        label_map = {"invoice": 0, "contract": 1, "receipt": 2}

        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2
        )

        # --- 2. Tokenize Data ---
        model_name = "distilbert-base-uncased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        train_encodings = tokenizer(train_texts, truncation=True, padding=True)
        val_encodings = tokenizer(val_texts, truncation=True, padding=True)
        train_dataset = DocDataset(train_encodings, train_labels)
        val_dataset = DocDataset(val_encodings, val_labels)

        # --- 3. Configure Trainer ---
        model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(label_map))
        training_args = TrainingArguments(
            output_dir='./models/results',
            num_train_epochs=3,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            logging_dir='./logs',
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset
        )

        # --- 4. Train and Save Model ---
        trainer.train()
        output_model_dir = './models/custom_classifier'
        model.save_pretrained(output_model_dir)
        tokenizer.save_pretrained(output_model_dir)

        self.stdout.write(self.style.SUCCESS(f"Training complete. Model saved to {output_model_dir}")) 