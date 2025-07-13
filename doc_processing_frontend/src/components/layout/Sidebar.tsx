
import React from 'react';
import { Link, useSearchParams, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  BarChart3, 
  Settings, 
  HelpCircle,
  Upload,
  CheckCircle2,
  Clock,
  AlertCircle,
  Filter,
  Zap,
  Users
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';
import type { StatusCounts } from './MainLayout';

type SidebarProps = {
  className?: string;
  statusCounts: StatusCounts;
};

const DOCUMENT_TYPES = [
  'All',
  'Advertisement', 
  'Contract',
  'Email',
  'Form',
  'Invoice',
  'Letter',
  'Receipt',
  'Resume'
];

const Sidebar = ({ className, statusCounts }: SidebarProps) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const currentType = searchParams.get('type') || 'All';

  const handleTypeChange = (type: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (type === 'All') {
      newParams.delete('type');
    } else {
      newParams.set('type', type);
    }
    setSearchParams(newParams);
  };

  // Helper function to determine if a route is active
  const isActiveRoute = (path: string) => {
    // For root path, check if we're exactly at '/' or '/dashboard'
    if (path === '/') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname.startsWith(path);
  };

  // Helper function to get navigation link classes
  const getNavLinkClasses = (path: string) => {
    const baseClasses = "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors";
    const activeClasses = "bg-accent text-accent-foreground";
    const inactiveClasses = "hover:bg-accent hover:text-accent-foreground";
    
    return cn(baseClasses, isActiveRoute(path) ? activeClasses : inactiveClasses);
  };

  return (
    <aside className={cn("pb-12 w-64 border-r hidden md:block", className)}>
      <div className="space-y-4 py-4">
        <div className="px-4 py-2">
          <h2 className="mb-2 px-2 text-lg font-semibold">Navigation</h2>
          <div className="space-y-1">
            <Link to="/" className={getNavLinkClasses('/')}>
              <LayoutDashboard className="h-4 w-4" />
              <span>Dashboard</span>
            </Link>
            
            <Link to="/documents" className={getNavLinkClasses('/documents')}>
              <FileText className="h-4 w-4" />
              <span>Documents</span>
            </Link>
            
            <Link to="/upload" className={getNavLinkClasses('/upload')}>
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </Link>
            
            <Link to="/approvals" className={getNavLinkClasses('/approvals')}>
              <Users className="h-4 w-4" />
              <span>Approvals</span>
            </Link>
            
            <Link to="/integrations" className={getNavLinkClasses('/integrations')}>
              <Zap className="h-4 w-4" />
              <span>Integrations</span>
            </Link>
            
            <Link to="/analytics" className={getNavLinkClasses('/analytics')}>
              <BarChart3 className="h-4 w-4" />
              <span>Analytics</span>
            </Link>
          </div>
        </div>
        
        <div className="px-4 py-2">
          <h2 className="mb-2 px-2 text-lg font-semibold">Document Status</h2>
          <div className="space-y-1">
            <Link to="/documents?status=processed" className={getNavLinkClasses('/documents?status=processed')}>
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Processed</span>
              </div>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{statusCounts.processed}</span>
            </Link>
            
            <Link to="/documents?status=processing" className={getNavLinkClasses('/documents?status=processing')}>
              <div className="flex items-center gap-3">
                <Clock className="h-4 w-4 text-blue-500" />
                <span>Processing</span>
              </div>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{statusCounts.processing}</span>
            </Link>
            
            <Link to="/documents?status=error" className={getNavLinkClasses('/documents?status=error')}>
              <div className="flex items-center gap-3">
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span>Error</span>
              </div>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{statusCounts.error}</span>
            </Link>
          </div>
        </div>
        
        <div className="px-4 py-2">
          <h2 className="mb-2 px-2 text-lg font-semibold">Filter by Type</h2>
          <div className="px-2">
            <Select value={currentType} onValueChange={handleTypeChange}>
              <SelectTrigger className="w-full">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  <SelectValue placeholder="Select type" />
                </div>
              </SelectTrigger>
              <SelectContent>
                {DOCUMENT_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
      
      <div className="mt-auto px-4 py-2">
        <div className="space-y-1">
          <Link to="/settings" className={getNavLinkClasses('/settings')}>
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </Link>
          
          <Link to="/help" className={getNavLinkClasses('/help')}>
            <HelpCircle className="h-4 w-4" />
            <span>Help & Support</span>
          </Link>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
