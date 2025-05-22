
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import DataExtractionPreview from '@/components/processing/DataExtractionPreview';
import { extractDocumentData, ExtractionResult } from '@/services/mock.service';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

// We're simulating that a document with ID "1" has been uploaded
const DEMO_DOCUMENT_ID = "1";

const DataExtractionView = () => {
  const [loading, setLoading] = useState(false);
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);

  const handleExtractData = async () => {
    setLoading(true);
    try {
      const data = await extractDocumentData(DEMO_DOCUMENT_ID);
      setExtractionResult(data);
    } catch (error) {
      toast.error('Failed to extract data from document');
      console.error('Extraction error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>Document Data Extraction</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="extraction">
          <TabsList>
            <TabsTrigger value="extraction">Extraction</TabsTrigger>
            <TabsTrigger value="validation">Validation</TabsTrigger>
            <TabsTrigger value="schema">Schema</TabsTrigger>
          </TabsList>
          
          <TabsContent value="extraction" className="pt-6">
            {!extractionResult ? (
              <div className="flex flex-col items-center justify-center py-8 space-y-4">
                <div className="text-center max-w-md">
                  <h3 className="text-lg font-medium mb-2">Extract Data from Document</h3>
                  <p className="text-muted-foreground mb-4">
                    AI will analyze the document and extract structured data for processing
                  </p>
                  <Button 
                    onClick={handleExtractData} 
                    disabled={loading} 
                    className="flex items-center"
                  >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {loading ? 'Processing...' : 'Extract Data'}
                  </Button>
                </div>
              </div>
            ) : (
              <DataExtractionPreview 
                documentType={extractionResult.documentType}
                fields={extractionResult.fields}
              />
            )}
          </TabsContent>
          
          <TabsContent value="validation" className="pt-6 text-center">
            <div className="py-8">
              <h3 className="text-lg font-medium mb-2">Data Validation</h3>
              <p className="text-muted-foreground">
                After extraction, validate and correct any misidentified fields
              </p>
            </div>
          </TabsContent>
          
          <TabsContent value="schema" className="pt-6 text-center">
            <div className="py-8">
              <h3 className="text-lg font-medium mb-2">Document Schema</h3>
              <p className="text-muted-foreground">
                Configure which fields should be extracted from each document type
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default DataExtractionView;
