
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle } from 'lucide-react';

interface ExtractedField {
  name: string;
  value: string;
  confidence: number;
  isValid: boolean;
}

interface DataExtractionPreviewProps {
  documentType: string;
  fields: ExtractedField[];
}

const DataExtractionPreview = ({ documentType, fields }: DataExtractionPreviewProps) => {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <CardTitle>Data Extraction Results</CardTitle>
          <Badge>{documentType}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {fields.map((field, index) => (
            <div key={index} className="border rounded-md p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-sm">{field.name}</h4>
                <div className="flex items-center gap-2">
                  {field.isValid ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                  <span className="text-xs font-medium">
                    {field.confidence}% confidence
                  </span>
                </div>
              </div>
              <p className={`text-sm ${field.isValid ? '' : 'text-red-500'}`}>
                {field.value}
              </p>
              {!field.isValid && (
                <p className="text-xs text-red-500 mt-1">
                  This field requires manual verification
                </p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default DataExtractionPreview;
