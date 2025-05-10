
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { AlertCircle, FileText, Copy } from 'lucide-react';
import { toast } from 'sonner';
import { DocumentService } from '@/services/document.service';

interface DocumentSummarizerProps {
  documentId?: string;
  documentText?: string;
}

const DocumentSummarizer = ({ documentId, documentText }: DocumentSummarizerProps) => {
  const [summarizing, setSummarizing] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSummarize = async () => {
    if (!documentText && !documentId) {
      toast.error('No document content available to summarize');
      return;
    }

    setSummarizing(true);
    setError(null);
    
    try {
      // Use the document service to summarize
      if (documentId) {
        const result = await DocumentService.summarizeDocument(documentId);
        setSummary(result.summary);
        toast.success('Document successfully summarized');
      } else if (documentText) {
        // If we only have text but no document ID, use a mock summary
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const mockSummary = `Executive Summary:\n\n` +
          `This document discusses key financial metrics for Q3 2023, highlighting a 15% increase in revenue compared to Q2. ` +
          `Major points include:\n\n` +
          `• Revenue growth primarily driven by expansion in Asian markets\n` +
          `• Operating costs reduced by 8% due to automation initiatives\n` +
          `• New product line exceeded sales targets by 22%\n` +
          `• Customer retention improved to 94% (up from 89%)\n\n` +
          `The document recommends continued investment in automation and expansion of the product line to additional markets in Q4.`;
        
        setSummary(mockSummary);
        toast.success('Document successfully summarized (using mock data)');
      }
    } catch (err) {
      console.error('Error summarizing document:', err);
      setError('Failed to summarize document. Please try again later.');
      toast.error('Failed to summarize document');
    } finally {
      setSummarizing(false);
    }
  };

  const copyToClipboard = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      toast.success('Summary copied to clipboard');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Document Summarization
        </CardTitle>
        <CardDescription>
          Extract key information and generate concise summaries from complex documents
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Button 
            onClick={handleSummarize} 
            disabled={summarizing}
            className="w-full"
          >
            {summarizing ? 'Summarizing...' : 'Generate Document Summary'}
          </Button>

          {error && (
            <div className="bg-red-50 text-red-800 p-3 rounded-md flex items-start gap-2">
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}

          {summary && (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h4 className="font-medium text-sm">Generated Summary</h4>
                <Button
                  variant="ghost" 
                  size="sm" 
                  className="h-8 gap-1"
                  onClick={copyToClipboard}
                >
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy</span>
                </Button>
              </div>
              <Textarea
                value={summary}
                readOnly
                className="min-h-[200px] font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                This summarization is powered by AI and may not capture all nuances of the original document.
                Always review the full document for critical decisions.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default DocumentSummarizer;
