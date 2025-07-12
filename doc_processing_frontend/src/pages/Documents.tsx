import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import DocumentGrid from '@/components/documents/DocumentGrid';
import DocumentDetailView from '@/components/documents/DocumentDetailView';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  Upload, 
  Filter,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchDocuments } from '@/lib/api';

const Documents = () => {
  const [searchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [isDetailViewOpen, setIsDetailViewOpen] = useState(false);
  
  // Get filters from URL parameters
  const statusFilter = searchParams.get('status');
  const typeFilter = searchParams.get('type');
  
  // Fetch documents from API using React Query
  const { data = [], isLoading, isError } = useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments,
  });

  // Handle document selection for viewing details
  const handleDocumentClick = (document: any) => {
    setSelectedDocument(document);
    setIsDetailViewOpen(true);
  };

  // Handle loading state
  if (isLoading) {
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
                disabled
              />
            </div>
            <Button variant="outline" size="icon" disabled>
              <Filter className="h-4 w-4" />
              <span className="sr-only">Filter</span>
            </Button>
            <Button variant="outline" size="icon" disabled>
              <SortAsc className="h-4 w-4" />
              <span className="sr-only">Sort</span>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, index) => (
              <Skeleton key={index} className="h-48 w-full" />
            ))}
          </div>
        </div>
      </MainLayout>
    );
  }

  // Handle error state
  if (isError) {
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
          
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center space-y-2">
              <p className="text-destructive font-medium">Failed to load documents.</p>
              <p className="text-muted-foreground">Please ensure the backend server is running.</p>
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Filter and sort live data with useMemo for performance
  const filteredDocuments = useMemo(() => {
    return data
      .filter(doc => {
        // Search filter
        const matchesSearch = doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
          doc.type.toLowerCase().includes(searchQuery.toLowerCase());
        
        // Status filter from URL
        const matchesStatus = !statusFilter || doc.status === statusFilter;
        
        // Type filter from URL
        const matchesType = !typeFilter || typeFilter === 'All' || 
          doc.document_type?.toLowerCase() === typeFilter.toLowerCase() ||
          doc.type?.toLowerCase() === typeFilter.toLowerCase();
          
        return matchesSearch && matchesStatus && matchesType;
      })
      .sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return sortOrder === 'asc' 
          ? dateA.getTime() - dateB.getTime() 
          : dateB.getTime() - dateA.getTime();
      });
  }, [data, searchQuery, sortOrder, statusFilter, typeFilter]);

  // Get current filter display text
  const getFilterDisplayText = () => {
    const filters = [];
    if (statusFilter) filters.push(`Status: ${statusFilter}`);
    if (typeFilter) filters.push(`Type: ${typeFilter}`);
    return filters.length > 0 ? ` (${filters.join(', ')})` : '';
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Documents{getFilterDisplayText()}
            </h1>
            <p className="text-muted-foreground">
              View and manage your processed documents
              {filteredDocuments.length !== data.length && (
                <span className="ml-1">({filteredDocuments.length} of {data.length} shown)</span>
              )}
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
            <DocumentGrid documents={filteredDocuments} onDocumentClick={handleDocumentClick} />
          </TabsContent>
          <TabsContent value="processed" className="pt-4">
            <DocumentGrid documents={filteredDocuments.filter(d => d.status === 'processed')} onDocumentClick={handleDocumentClick} />
          </TabsContent>
          <TabsContent value="processing" className="pt-4">
            <DocumentGrid documents={filteredDocuments.filter(d => d.status === 'processing')} onDocumentClick={handleDocumentClick} />
          </TabsContent>
          <TabsContent value="error" className="pt-4">
            <DocumentGrid documents={filteredDocuments.filter(d => d.status === 'error')} onDocumentClick={handleDocumentClick} />
          </TabsContent>
        </Tabs>
        
        {/* Document Detail View Modal */}
        <DocumentDetailView 
          document={selectedDocument} 
          isOpen={isDetailViewOpen} 
          onClose={() => setIsDetailViewOpen(false)} 
        />
      </div>
    </MainLayout>
  );
};

export default Documents;
