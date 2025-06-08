
import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import DocumentGrid from '@/components/documents/DocumentGrid';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  Upload, 
  Filter,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { Link } from 'react-router-dom';

const allDocuments = [
  {
    id: '1',
    filename: 'Invoice-May2025-12345.pdf',
    type: 'invoice' as const,
    status: 'processed' as const,
    date: 'May 8, 2025',
    confidence: 98
  },
  {
    id: '2',
    filename: 'Contract-ServiceAgreement.pdf',
    type: 'contract' as const,
    status: 'processed' as const,
    date: 'May 7, 2025',
    confidence: 95
  },
  {
    id: '3',
    filename: 'Receipt-Office-Supplies.jpg',
    type: 'receipt' as const,
    status: 'processing' as const,
    date: 'May 8, 2025'
  },
  {
    id: '4',
    filename: 'Invoice-April2025-45678.pdf',
    type: 'invoice' as const,
    status: 'processed' as const,
    date: 'Apr 29, 2025',
    confidence: 92
  },
  {
    id: '5',
    filename: 'Contract-NDA-Client123.pdf',
    type: 'contract' as const,
    status: 'error' as const,
    date: 'May 6, 2025'
  },
  {
    id: '6',
    filename: 'Receipt-Travel-Expenses.jpg',
    type: 'receipt' as const,
    status: 'processed' as const,
    date: 'May 3, 2025',
    confidence: 90
  },
  {
    id: '7',
    filename: 'Invoice-March2025-98765.pdf',
    type: 'invoice' as const,
    status: 'processed' as const,
    date: 'Mar 15, 2025',
    confidence: 97
  },
  {
    id: '8',
    filename: 'Report-Q1-2025.pdf',
    type: 'report' as const,
    status: 'processed' as const,
    date: 'Apr 10, 2025',
    confidence: 94
  }
];

const Documents = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  const filteredDocuments = allDocuments
    .filter(doc => 
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.type.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      const dateA = new Date(a.date);
      const dateB = new Date(b.date);
      return sortOrder === 'asc' 
        ? dateA.getTime() - dateB.getTime() 
        : dateB.getTime() - dateA.getTime();
    });

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
            <p className="text-muted-foreground">
              View and manage your processed documents
            </p>
          </div>
          <Link to="/upload">
            <Button>
              <Upload className="h-4 w-4 mr-2" />
              Upload New
            </Button>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search by filename or document type"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
            <span className="sr-only">Filter</span>
          </Button>
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          >
            {sortOrder === 'asc' ? (
              <SortAsc className="h-4 w-4" />
            ) : (
              <SortDesc className="h-4 w-4" />
            )}
            <span className="sr-only">Sort</span>
          </Button>
        </div>

        <Tabs defaultValue="all">
          <TabsList>
            <TabsTrigger value="all">All Documents</TabsTrigger>
            <TabsTrigger value="processed">Processed</TabsTrigger>
            <TabsTrigger value="processing">Processing</TabsTrigger>
            <TabsTrigger value="error">Error</TabsTrigger>
          </TabsList>
          <TabsContent value="all" className="pt-4">
            <DocumentGrid documents={filteredDocuments} />
          </TabsContent>
          <TabsContent value="processed" className="pt-4">
            <DocumentGrid documents={filteredDocuments.filter(d => d.status === 'processed')} />
          </TabsContent>
          <TabsContent value="processing" className="pt-4">
            <DocumentGrid documents={filteredDocuments.filter(d => d.status === 'processing')} />
          </TabsContent>
          <TabsContent value="error" className="pt-4">
            <DocumentGrid documents={filteredDocuments.filter(d => d.status === 'error')} />
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
};

export default Documents;
