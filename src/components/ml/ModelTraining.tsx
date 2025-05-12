
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { Brain, Activity, BarChart3, HardDrive } from 'lucide-react';
import { MLService, ModelStats } from '@/services/ml.service';

const ModelTraining = () => {
  const [training, setTraining] = useState(false);
  const [progress, setProgress] = useState(0);
  const [modelStats, setModelStats] = useState<ModelStats | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadModelStats();
  }, []);
  
  const loadModelStats = async () => {
    setLoading(true);
    try {
      const stats = await MLService.getModelStats();
      setModelStats(stats);
    } catch (error) {
      console.error('Failed to load model stats:', error);
      toast.error('Unable to load model statistics');
    } finally {
      setLoading(false);
    }
  };
  
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
      
      // Refresh stats after training
      await loadModelStats();
      
    } catch (error) {
      console.error('Error during model training:', error);
      toast.error('Failed to train model. Please try again.');
    } finally {
      setTimeout(() => {
        setTraining(false);
      }, 1000);
    }
  };
  
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            ML Model Training
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center py-6">
            <Progress value={100} className="w-2/3 h-2 animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          ML Model Training
        </CardTitle>
        <CardDescription>
          Train the document classification model using images from your media directory
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            The ML model improves by learning from the images in your media directory. 
            Regular training ensures accurate document categorization and data extraction.
          </p>
          
          {modelStats?.mediaDirectory && (
            <div className="bg-muted/50 p-3 rounded-lg flex items-center gap-2 text-sm">
              <HardDrive className="h-4 w-4 text-blue-500" />
              <span className="text-xs text-muted-foreground overflow-hidden text-ellipsis">
                Media Directory: {modelStats.mediaDirectory}
              </span>
            </div>
          )}
          
          <div className="bg-muted/50 p-4 rounded-lg space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">Model Status</span>
              </div>
              <span className={`text-sm px-2 py-0.5 rounded-full ${
                modelStats?.modelExists 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-amber-100 text-amber-800'
              }`}>
                {modelStats?.modelExists ? 'Active' : 'Not Trained'}
              </span>
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Model Accuracy</span>
                <span>{modelStats?.accuracy || 0}%</span>
              </div>
              <Progress value={modelStats?.accuracy || 0} className="h-2" />
            </div>
            
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>
                {modelStats?.lastTrainingDate 
                  ? `Last trained: ${new Date(modelStats?.lastTrainingDate).toLocaleDateString()}`
                  : 'Not trained yet'}
              </span>
              <span>{modelStats?.totalDocumentsProcessed || 0} documents available</span>
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
