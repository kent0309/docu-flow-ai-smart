
import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { fetchDocuments } from '@/lib/api';

interface MainLayoutProps {
  children: React.ReactNode;
}

export interface StatusCounts {
  processed: number;
  processing: number;
  error: number;
}

const MainLayout = ({ children }: MainLayoutProps) => {
  // Fetch documents from API using React Query
  const { data: documents = [] } = useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments,
  });

  // Calculate status counts dynamically from fetched data
  const statusCounts: StatusCounts = useMemo(() => {
    return {
      processed: documents.filter(doc => doc.status === 'processed').length,
      processing: documents.filter(doc => doc.status === 'processing').length,
      error: documents.filter(doc => doc.status === 'error').length,
    };
  }, [documents]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar statusCounts={statusCounts} />
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
