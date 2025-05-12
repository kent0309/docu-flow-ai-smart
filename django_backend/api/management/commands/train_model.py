
from django.core.management.base import BaseCommand
from api.services.ml_document_classifier import document_classifier

class Command(BaseCommand):
    help = 'Train the document classification ML model'

    def handle(self, *args, **options):
        self.stdout.write('Starting model training...')
        
        try:
            success = document_classifier.update_model(force_train=True)
            
            if success:
                self.stdout.write(self.style.SUCCESS('Model training completed successfully'))
            else:
                self.stdout.write(self.style.WARNING(
                    'Training completed but model was not updated. Not enough data or current model performs better.'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error training model: {e}'))
