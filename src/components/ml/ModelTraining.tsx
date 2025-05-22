
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrainModel } from 'lovable-icon';
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
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-4 w-4"
                >
                  <path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z" />
                  <path d="M7 7h.01" />
                </svg>
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
