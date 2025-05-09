
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import DataExtractionPreview from '@/components/processing/DataExtractionPreview';
import DocumentSummarizer from '@/components/documents/DocumentSummarizer';

// Sample extracted data for demo purposes
const sampleInvoiceData = {
  documentType: 'Invoice',
  fields: [
    { name: 'Invoice Number', value: 'INV-2023-0042', confidence: 98, isValid: true },
    { name: 'Date', value: '2023-05-15', confidence: 96, isValid: true },
    { name: 'Vendor', value: 'Global Supplies Inc.', confidence: 93, isValid: true },
    { name: 'Amount Due', value: '$1,245.67', confidence: 97, isValid: true },
    { name: 'Tax ID', value: 'TX-93829384', confidence: 89, isValid: true },
    { name: 'Payment Terms', value: 'Net 30', confidence: 95, isValid: true },
  ]
};

const sampleReportData = {
  documentType: 'Financial Report',
  fields: [
    { name: 'Report Title', value: 'Q3 Financial Performance Analysis', confidence: 99, isValid: true },
    { name: 'Period', value: 'July 1 - September 30, 2023', confidence: 97, isValid: true },
    { name: 'Total Revenue', value: '$2,456,789.00', confidence: 95, isValid: true },
    { name: 'Net Profit', value: '$687,452.18', confidence: 96, isValid: true },
    { name: 'YoY Growth', value: '15.7%', confidence: 92, isValid: true },
    { name: 'Author', value: 'Finance Department', confidence: 74, isValid: false },
  ]
};

// Sample text for summarization demo
const sampleReportText = `
QUARTERLY FINANCIAL REPORT
Q3 2023
Prepared by: Finance Department
Date: October 10, 2023

EXECUTIVE SUMMARY
This report presents the financial performance of the company for the third quarter of 2023. Overall revenue increased by 15% compared to Q2, primarily driven by strong performance in the Asian markets and successful launch of the new product line. Operating costs were reduced by 8% due to automation initiatives implemented in Q2. The new product line exceeded sales targets by 22%.

FINANCIAL HIGHLIGHTS
Revenue: $2,456,789.00 (15% increase from Q2)
Net Profit: $687,452.18 (23% increase from Q2)
Operating Costs: $1,125,000.00 (8% decrease from Q2)
Gross Margin: 42% (up from 37% in Q2)
Customer Acquisition Cost: $45.78 (down from $52.35 in Q2)
Customer Lifetime Value: $950.25 (up from $875.50 in Q2)
Customer Retention Rate: 94% (up from 89% in Q2)

REGIONAL PERFORMANCE
North America: $980,500.00 (8% increase)
Europe: $725,300.00 (5% increase)
Asia: $520,989.00 (48% increase)
Others: $230,000.00 (12% increase)

PRODUCT LINE PERFORMANCE
Core Services: $1,215,000.00 (5% increase)
Premium Solutions: $720,789.00 (12% increase)
New Innovation Line: $521,000.00 (exceeded forecast by 22%)

KEY ACCOMPLISHMENTS
1. Successfully launched the New Innovation Line in 7 markets
2. Reduced customer service response time by 35% through AI implementation
3. Completed digital transformation of the supply chain management process
4. Established partnerships with 3 new major distribution channels

CHALLENGES
1. Increased competition in European markets leading to price pressure
2. Supply chain disruptions in certain regions
3. Currency fluctuations impacting profit margins in international operations
4. Talent acquisition challenges in technical departments

OUTLOOK AND RECOMMENDATIONS
Based on Q3 performance, we project continued growth in Q4, with estimated revenue of $2,700,000.00. To capitalize on current momentum, we recommend:

1. Accelerating expansion of the New Innovation Line to additional markets
2. Increasing investment in automation initiatives to further reduce operating costs
3. Implementing the proposed customer loyalty program to improve retention rates
4. Exploring strategic acquisition opportunities in the European market to combat increased competition

The finance team will continue to monitor market conditions and provide updates as necessary.

END OF REPORT
`;

const DataExtractionView = () => {
  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>Data Extraction & Summarization</CardTitle>
        <CardDescription>
          View extracted information and AI-generated summaries from your documents
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="extracted-data" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="extracted-data">Extracted Data</TabsTrigger>
            <TabsTrigger value="summarization">Document Summary</TabsTrigger>
          </TabsList>
          
          <TabsContent value="extracted-data" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Extracted Information</h3>
              <Badge variant="outline" className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                Processed
              </Badge>
            </div>
            
            <Tabs defaultValue="invoice">
              <TabsList>
                <TabsTrigger value="invoice">Invoice Example</TabsTrigger>
                <TabsTrigger value="report">Report Example</TabsTrigger>
              </TabsList>
              <TabsContent value="invoice" className="pt-4">
                <DataExtractionPreview 
                  documentType={sampleInvoiceData.documentType} 
                  fields={sampleInvoiceData.fields}
                />
              </TabsContent>
              <TabsContent value="report" className="pt-4">
                <DataExtractionPreview 
                  documentType={sampleReportData.documentType} 
                  fields={sampleReportData.fields}
                />
              </TabsContent>
            </Tabs>
          </TabsContent>
          
          <TabsContent value="summarization">
            <DocumentSummarizer documentText={sampleReportText} />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default DataExtractionView;
