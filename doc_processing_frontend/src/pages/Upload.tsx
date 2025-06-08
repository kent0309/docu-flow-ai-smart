
import React from 'react';
import Layout from '@/components/layout/Layout';
import FileUploader from '@/components/documents/FileUploader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  Zap, 
  Shield, 
  Clock,
  CheckCircle
} from 'lucide-react';

const Upload = () => {
  const supportedFormats = [
    { type: 'PDF', description: 'Portable Document Format', icon: FileText },
    { type: 'JPG/JPEG', description: 'Image files', icon: FileText },
    { type: 'PNG', description: 'Image files', icon: FileText },
    { type: 'DOC/DOCX', description: 'Microsoft Word documents', icon: FileText },
  ];

  const processingSteps = [
    { step: 1, title: 'Document Upload', description: 'Securely upload your documents', icon: FileText },
    { step: 2, title: 'AI Analysis', description: 'Advanced AI processes your documents', icon: Zap },
    { step: 3, title: 'Data Extraction', description: 'Key information is extracted automatically', icon: Shield },
    { step: 4, title: 'Quality Check', description: 'Results are validated for accuracy', icon: CheckCircle },
  ];

  return (
    <Layout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Upload Documents</h1>
          <p className="text-muted-foreground mt-1">
            Upload documents for AI-powered processing and data extraction
          </p>
        </div>

        <Tabs defaultValue="upload" className="w-full">
          <TabsList>
            <TabsTrigger value="upload">Upload Files</TabsTrigger>
            <TabsTrigger value="formats">Supported Formats</TabsTrigger>
            <TabsTrigger value="process">How It Works</TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="pt-6">
            <div className="grid gap-6 grid-cols-1 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <FileUploader />
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
                        <option value="fr">French</option>
                        <option value="de">German</option>
                      </select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Processing Priority</label>
                      <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                        <option value="normal">Normal (Free)</option>
                        <option value="high">High Priority (+$1)</option>
                        <option value="urgent">Urgent (+$5)</option>
                      </select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Document Type</label>
                      <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                        <option value="auto">Auto-detect</option>
                        <option value="invoice">Invoice</option>
                        <option value="contract">Contract</option>
                        <option value="receipt">Receipt</option>
                        <option value="report">Report</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input 
                        type="checkbox" 
                        id="notifications" 
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                        defaultChecked
                      />
                      <label htmlFor="notifications" className="text-sm">
                        Email me when processing completes
                      </label>
                    </div>

                    <div className="p-4 bg-muted rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="h-4 w-4 text-primary" />
                        <span className="font-medium text-sm">Processing Time</span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Average processing time: 30-45 seconds per document
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="formats" className="pt-6">
            <Card>
              <CardHeader>
                <CardTitle>Supported File Formats</CardTitle>
                <CardDescription>
                  Our AI system can process the following document types
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                  {supportedFormats.map((format) => (
                    <div key={format.type} className="flex items-center gap-4 p-4 border rounded-lg">
                      <div className="rounded-md bg-primary/10 p-2">
                        <format.icon className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-medium">{format.type}</h3>
                        <p className="text-sm text-muted-foreground">{format.description}</p>
                      </div>
                      <Badge variant="secondary" className="ml-auto">
                        Supported
                      </Badge>
                    </div>
                  ))}
                </div>
                
                <div className="mt-6 p-4 bg-muted rounded-lg">
                  <h4 className="font-medium mb-2">File Size Limits</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Maximum file size: 10MB</li>
                    <li>• Maximum files per upload: 20</li>
                    <li>• Supported image resolutions: Up to 4K</li>
                    <li>• PDF pages: Up to 50 pages per document</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="process" className="pt-6">
            <Card>
              <CardHeader>
                <CardTitle>How Document Processing Works</CardTitle>
                <CardDescription>
                  Our AI-powered system processes your documents in four simple steps
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-8">
                  {processingSteps.map((step, index) => (
                    <div key={step.step} className="flex items-start gap-4">
                      <div className="rounded-full bg-primary text-primary-foreground w-8 h-8 flex items-center justify-center text-sm font-medium">
                        {step.step}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <step.icon className="h-5 w-5 text-primary" />
                          <h3 className="font-medium">{step.title}</h3>
                        </div>
                        <p className="text-muted-foreground text-sm">{step.description}</p>
                      </div>
                      {index < processingSteps.length - 1 && (
                        <div className="absolute left-4 mt-8 w-px h-8 bg-border"></div>
                      )}
                    </div>
                  ))}
                </div>

                <div className="mt-8 grid gap-4 grid-cols-1 md:grid-cols-3">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">95%+</div>
                    <div className="text-sm text-muted-foreground">Accuracy Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">30s</div>
                    <div className="text-sm text-muted-foreground">Avg Processing Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">24/7</div>
                    <div className="text-sm text-muted-foreground">Service Availability</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Upload;
