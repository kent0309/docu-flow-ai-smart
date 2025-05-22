
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrainModel } from '@/components/lovable-icon';
import { trainModel } from '@/services/mock.service';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

const ModelTraining = () => {
  const [isTraining, setIsTraining] = useState(false);

  const handleTrainModel = async () => {
    setIsTraining(true);
    
    try {
      await trainModel();
      toast.success("Model training completed successfully!");
    } catch (error) {
      console.error("Model training error:", error);
      toast.error("Error training the model");
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Train AI Model</CardTitle>
        <CardDescription>
          Improve document classification accuracy
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-sm">
            <p>Train the AI model with new documents to improve classification accuracy and data extraction.</p>
          </div>
          
          <Button 
            variant="default" 
            className="w-full flex items-center justify-center gap-2"
            onClick={handleTrainModel}
            disabled={isTraining}
          >
            {isTraining ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Training...</span>
              </>
            ) : (
              <>
                <TrainModel className="h-4 w-4" />
                <span>Train Model</span>
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ModelTraining;
