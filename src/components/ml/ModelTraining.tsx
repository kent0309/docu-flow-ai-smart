
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { Brain, Activity, BarChart3 } from 'lucide-react';
import { MLService } from '@/services/ml.service';

const ModelTraining = () => {
  const [training, setTraining] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const handleTrainModel = async () => {
    setTraining(true);
    setProgress(0);
    
    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return 95;
        }
        return prev + Math.floor(Math.random() * 10) + 1;
      });
    }, 800);
    
    try {
      // Call the ML service to train the model
      const result = await MLService.trainModel();
      
      // Complete the progress bar and show success
      clearInterval(progressInterval);
      setProgress(100);
      
      if (result.status === 'success') {
        toast.success(result.message || 'Model training completed successfully');
      } else {
        toast.warning(result.message || 'Training completed with warnings');
      }
      
    } catch (error) {
      console.error('Error during model training:', error);
      toast.error('Failed to train model. Please try again.');
    } finally {
      setTimeout(() => {
        setTraining(false);
      }, 1000);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          ML Model Training
        </CardTitle>
        <CardDescription>
          Train the document classification model using your dataset
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            The ML model improves by learning from the documents you process. 
            Regular training ensures accurate document categorization and data extraction.
          </p>
          
          <div className="bg-muted/50 p-4 rounded-lg space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">Model Status</span>
              </div>
              <span className="text-sm bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                Active
              </span>
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Model Accuracy</span>
                <span>92.5%</span>
              </div>
              <Progress value={92.5} className="h-2" />
            </div>
            
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Last trained: 10 days ago</span>
              <span>157 documents processed</span>
            </div>
          </div>
          
          {training ? (
            <div className="space-y-2">
              <div className="text-center font-medium text-sm">
                Training in Progress...
              </div>
              <Progress value={progress} className="h-2" />
              <div className="text-xs text-center text-muted-foreground">
                {progress >= 100 ? 'Complete!' : `${progress}% - Processing training data`}
              </div>
            </div>
          ) : (
            <Button 
              onClick={handleTrainModel} 
              className="w-full"
            >
              Train Model Now
            </Button>
          )}
          
          <div className="flex justify-between text-xs text-muted-foreground pt-2">
            <Button 
              variant="link" 
              size="sm" 
              className="h-auto p-0 text-xs flex items-center" 
              asChild
            >
              <a href="#">
                <BarChart3 className="h-3 w-3 mr-1" />
                View Detailed Analytics
              </a>
            </Button>
            <Button 
              variant="link" 
              size="sm" 
              className="h-auto p-0 text-xs" 
              asChild
            >
              <a href="#">Configure Training Settings</a>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ModelTraining;
