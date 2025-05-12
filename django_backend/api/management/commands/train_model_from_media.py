
from django.core.management.base import BaseCommand
from api.services.document_processor import train_ml_model
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Train the document classification ML model using images from media directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update the model even if performance is not improved',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        self.stdout.write('Starting model training with images from media directory...')
        
        try:
            # Call the training function
            success = train_ml_model()
            
            if success:
                self.stdout.write(self.style.SUCCESS(
                    'Model training completed successfully! The model has been updated.'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    'Training completed but model was not updated. Not enough data or current model performs better.'
                ))
            
            self.stdout.write('For better results, organize your images into folders named by document type')
            self.stdout.write('Example structure: media/invoices/, media/contracts/, etc.')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error training model: {e}'))
            logger.exception("Model training error")
