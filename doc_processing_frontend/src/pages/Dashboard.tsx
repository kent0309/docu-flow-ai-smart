import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import StatCard from '@/components/dashboard/StatCard';
import ProcessingStats from '@/components/dashboard/ProcessingStats';
import AIAccuracy from '@/components/dashboard/AIAccuracy';
import DocumentGrid from '@/components/documents/DocumentGrid';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowRight,
  Upload
} from 'lucide-react';
import { Link } from 'react-router-dom';

const recentDocuments = [
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
  }
];

const Dashboard = () => {
  return (
    <MainLayout>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              View and manage your document processing activities
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
          <StatCard
            title="Total Documents"
            value="1,248"
            icon={<FileText className="h-5 w-5 text-primary" />}
            description="Last 30 days"
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            title="Processing"
            value="3"
            icon={<Clock className="h-5 w-5 text-blue-500" />}
            description="Documents in queue"
          />
          <StatCard
            title="Processed"
            value="1,245"
            icon={<CheckCircle className="h-5 w-5 text-green-500" />}
            description="Successfully completed"
            trend={{ value: 8, isPositive: true }}
          />
          <StatCard
            title="Errors"
            value="5"
            icon={<AlertCircle className="h-5 w-5 text-red-500" />}
            description="Requires attention"
            trend={{ value: 2, isPositive: false }}
          />
        </div>

        <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
          <ProcessingStats />
          <AIAccuracy />
        </div>

        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Recent Documents</h2>
            <Link to="/documents">
              <Button variant="outline" size="sm" className="gap-1">
                <span>View All</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <DocumentGrid documents={recentDocuments} />
        </div>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
