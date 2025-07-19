import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import StatCard from '@/components/dashboard/StatCard';
import ProcessingStats from '@/components/dashboard/ProcessingStats';
import AIAccuracy from '@/components/dashboard/AIAccuracy';
import DocumentGrid from '@/components/documents/DocumentGrid';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowRight,
  Upload
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchDocuments, type Document } from '@/lib/api';
import DocumentPollingManager from '@/components/documents/DocumentPollingManager';

const Dashboard = () => {
  const [searchParams] = useSearchParams();
  
  // Fetch documents from API using React Query with same queryKey for caching
  // This reuses the same query as MainLayout, so it will be cached
  const { data: documents = [], isLoading, isError } = useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments,
  });

  // Get filters from URL parameters
  const typeFilter = searchParams.get('type');

  // Apply type filter to documents if present
  const filteredDocuments = useMemo(() => {
    if (!typeFilter || typeFilter === 'All') {
      return documents;
    }
    return documents.filter(doc => 
      doc.document_type?.toLowerCase() === typeFilter.toLowerCase() ||
      doc.type?.toLowerCase() === typeFilter.toLowerCase()
    );
  }, [documents, typeFilter]);

  // Calculate statistics dynamically from filtered data
  const stats = useMemo(() => {
    return {
      total: filteredDocuments.length,
      processing: filteredDocuments.filter(doc => doc.status === 'processing').length,
      processed: filteredDocuments.filter(doc => doc.status === 'processed').length,
      errors: filteredDocuments.filter(doc => doc.status === 'error').length,
    };
  }, [filteredDocuments]);

  // Get recent documents (latest 4) from filtered set
  const recentDocuments = useMemo(() => {
    return filteredDocuments.slice(0, 4);
  }, [filteredDocuments]);

  // Get filter display text
  const getFilterDisplayText = () => {
    return typeFilter ? ` - ${typeFilter}` : '';
  };

  // Prepare documents for polling (only processing ones)
  const processingDocuments = documents
    .filter(doc => doc.status === 'processing')
    .map(doc => ({
      id: doc.id,
      name: doc.filename,
      status: doc.status
    }));

  return (
    <MainLayout>
      {/* Document Polling Manager for real-time status updates */}
      <DocumentPollingManager documents={processingDocuments} />
      
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Dashboard{getFilterDisplayText()}
            </h1>
            <p className="text-muted-foreground">
              View and manage your document processing activities
              {typeFilter && (
                <span className="ml-1">({filteredDocuments.length} {typeFilter.toLowerCase()} documents)</span>
              )}
            </p>
          </div>
          <Link to="/upload">
            <Button>
              <Upload className="h-4 w-4 mr-2" />
              Upload Documents
            </Button>
          </Link>
        </div>

        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
          {isLoading ? (
            <>
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
            </>
          ) : (
            <>
              <StatCard
                title="Total Documents"
                value={stats.total.toString()}
                icon={<FileText className="h-5 w-5 text-primary" />}
                description={typeFilter ? `${typeFilter} documents` : "All documents"}
                trend={{ value: 12, isPositive: true }}
              />
              <StatCard
                title="Processing"
                value={stats.processing.toString()}
                icon={<Clock className="h-5 w-5 text-blue-500" />}
                description="Documents in queue"
              />
              <StatCard
                title="Processed"
                value={stats.processed.toString()}
                icon={<CheckCircle className="h-5 w-5 text-green-500" />}
                description="Successfully completed"
                trend={{ value: 8, isPositive: true }}
              />
              <StatCard
                title="Errors"
                value={stats.errors.toString()}
                icon={<AlertCircle className="h-5 w-5 text-red-500" />}
                description="Requires attention"
                trend={{ value: 2, isPositive: false }}
              />
            </>
          )}
        </div>

        <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
          <ProcessingStats />
          <AIAccuracy />
        </div>

        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">
              Recent Documents{typeFilter ? ` - ${typeFilter}` : ''}
            </h2>
            <Link to={`/documents${typeFilter ? `?type=${typeFilter}` : ''}`}>
              <Button variant="outline" size="sm" className="gap-1">
                <span>View All</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {Array.from({ length: 4 }).map((_, index) => (
                <Skeleton key={index} className="h-48 w-full" />
              ))}
            </div>
          ) : (
            <DocumentGrid documents={recentDocuments} />
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
