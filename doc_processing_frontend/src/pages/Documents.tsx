
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/layout/Layout';
import DocumentCard from '@/components/documents/DocumentCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { 
  Search, 
  Upload, 
  Filter,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { mockService } from '@/services/mockService';
import { Document, DocumentStatus } from '@/types';

const Documents = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [activeTab, setActiveTab] = useState('all');
  
  const { data: allDocuments = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: mockService.getDocuments,
  });

  // Filter and sort documents
  const filteredDocuments = React.useMemo(() => {
    let filtered = allDocuments;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(doc => 
        doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.type.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by tab
    if (activeTab !== 'all') {
      filtered = filtered.filter(doc => doc.status === activeTab);
    }

    // Sort by date
    filtered.sort((a, b) => {
      const dateA = new Date(a.uploadDate);
      const dateB = new Date(b.uploadDate);
      return sortOrder === 'asc' 
        ? dateA.getTime() - dateB.getTime() 
        : dateB.getTime() - dateA.getTime();
    });

    return filtered;
  }, [allDocuments, searchQuery, activeTab, sortOrder]);

  const getDocumentsByStatus = (status: DocumentStatus) => {
    return allDocuments.filter(doc => doc.status === status);
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
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

        {/* Search and filters */}
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
          </Button>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">
              All Documents ({allDocuments.length})
            </TabsTrigger>
            <TabsTrigger value="processed">
              Processed ({getDocumentsByStatus('processed').length})
            </TabsTrigger>
            <TabsTrigger value="processing">
              Processing ({getDocumentsByStatus('processing').length})
            </TabsTrigger>
            <TabsTrigger value="error">
              Error ({getDocumentsByStatus('error').length})
            </TabsTrigger>
            <TabsTrigger value="pending">
              Pending ({getDocumentsByStatus('pending').length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="pt-4">
            {filteredDocuments.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="rounded-full bg-muted p-6 mb-4">
                    <Search className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-xl font-medium mb-1">No documents found</h3>
                  <p className="text-muted-foreground max-w-sm">
                    {searchQuery 
                      ? `No documents match "${searchQuery}"`
                      : "Upload documents to start processing them with our AI system."
                    }
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {filteredDocuments.map((document) => (
                  <DocumentCard 
                    key={document.id} 
                    document={document}
                    onView={(id) => console.log('View document:', id)}
                    onDownload={(id) => console.log('Download document:', id)}
                  />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Documents;
