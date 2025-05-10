
import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import FileUploader from '@/components/documents/FileUploader';
import DataExtractionView from '@/components/documents/DataExtractionView';
import ModelTraining from '@/components/ml/ModelTraining';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const Upload = () => {
  const [showExtraction, setShowExtraction] = useState(false);

  // Callback for when files are processed successfully
  const handleFilesProcessed = () => {
    // In a real app, this would be triggered by actual file processing
    // For the demo, we'll just show the extraction section after "processing"
    setShowExtraction(true);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Upload Documents</h1>
          <p className="text-muted-foreground mt-1">
            Upload documents for AI-powered processing, data extraction, and summarization
          </p>
        </div>

        <Tabs defaultValue="upload" className="w-full">
          <TabsList>
            <TabsTrigger value="upload">Upload Files</TabsTrigger>
            <TabsTrigger value="scan">Scan Documents</TabsTrigger>
            <TabsTrigger value="email">Email Integration</TabsTrigger>
          </TabsList>
          <TabsContent value="upload" className="pt-4">
            <div className="grid gap-6 grid-cols-1 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Upload Files</CardTitle>
                    <CardDescription>
                      Supported formats: PDF, JPG, PNG, DOC, DOCX (Max 10MB per file)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <FileUploader onFilesProcessed={handleFilesProcessed} />
                  </CardContent>
                </Card>

                {showExtraction && <DataExtractionView />}
              </div>
              
              <div className="lg:col-span-1">
                <Card>
                  <CardHeader>
                    <CardTitle>Processing Options</CardTitle>
                    <CardDescription>
                      Configure how your documents should be processed
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Document Language</label>
                      <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                        <option value="auto">Auto-detect (Recommended)</option>
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="zh">Mandarin</option>
                        <option value="ms">Malay</option>
                      </select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Processing Priority</label>
                      <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                        <option value="normal">Normal</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                      </select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Workflow</label>
                      <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                        <option value="default">Default Processing</option>
                        <option value="invoice">Invoice Processing</option>
                        <option value="contract">Contract Analysis</option>
                        <option value="receipt">Receipt Processing</option>
                      </select>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input 
                        type="checkbox" 
                        id="notifications" 
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                      />
                      <label htmlFor="notifications" className="text-sm">
                        Email me when processing completes
                      </label>
                    </div>
                  </CardContent>
                </Card>
                
                <div className="mt-6">
                  <ModelTraining />
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="scan" className="pt-4">
            <Card>
              <CardHeader>
                <CardTitle>Scan Documents</CardTitle>
                <CardDescription>
                  Use your device camera or scanner to capture documents directly
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="rounded-full bg-muted p-6 mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                    <path d="M15 3h4a2 2 0 0 1 2 2v4"></path>
                    <path d="M13 21H5a2 2 0 0 1-2-2v-8"></path>
                    <path d="m21 15-5-5-5 5"></path>
                    <path d="M8 3H5a2 2 0 0 0-2 2v3"></path>
                  </svg>
                </div>
                <h3 className="text-xl font-medium mb-2">Coming Soon</h3>
                <p className="text-muted-foreground text-center max-w-md">
                  This feature is under development. Soon you'll be able to scan documents directly from your device.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="email" className="pt-4">
            <Card>
              <CardHeader>
                <CardTitle>Email Integration</CardTitle>
                <CardDescription>
                  Send documents to a dedicated email address for automatic processing
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="rounded-full bg-muted p-6 mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                    <rect width="16" height="13" x="4" y="5" rx="2"></rect>
                    <path d="m22 5-7.1 9.4a2 2 0 0 1-3.8 0L4 5"></path>
                    <path d="M22 5 12 13 2 5"></path>
                  </svg>
                </div>
                <h3 className="text-xl font-medium mb-2">Coming Soon</h3>
                <p className="text-muted-foreground text-center max-w-md">
                  This feature is under development. Soon you'll be able to email documents for automatic processing.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
};

export default Upload;
