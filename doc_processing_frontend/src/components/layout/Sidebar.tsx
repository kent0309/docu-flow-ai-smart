import React from 'react';
import { Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Workflow, 
  BarChart3, 
  Settings, 
  HelpCircle,
  Upload,
  CheckCircle2,
  Clock,
  AlertCircle,
  TagsIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

type SidebarProps = {
  className?: string;
};

const Sidebar = ({ className }: SidebarProps) => {
  return (
    <aside className={cn("pb-12 w-64 border-r hidden md:block", className)}>
      <div className="space-y-4 py-4">
        <div className="px-4 py-2">
          <h2 className="mb-2 px-2 text-lg font-semibold">Navigation</h2>
          <div className="space-y-1">
            <Link to="/" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium bg-accent text-accent-foreground">
              <LayoutDashboard className="h-4 w-4" />
              <span>Dashboard</span>
            </Link>
            
            <Link to="/documents" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <FileText className="h-4 w-4" />
              <span>Documents</span>
            </Link>
            
            <Link to="/upload" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </Link>
            
            <Link to="/workflows" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <Workflow className="h-4 w-4" />
              <span>Workflows</span>
            </Link>
            
            <Link to="/analytics" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <BarChart3 className="h-4 w-4" />
              <span>Analytics</span>
            </Link>
          </div>
        </div>
        
        <div className="px-4 py-2">
          <h2 className="mb-2 px-2 text-lg font-semibold">Document Status</h2>
          <div className="space-y-1">
            <Link to="/documents?status=processed" className="flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Processed</span>
              </div>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs">12</span>
            </Link>
            
            <Link to="/documents?status=processing" className="flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <div className="flex items-center gap-3">
                <Clock className="h-4 w-4 text-blue-500" />
                <span>Processing</span>
              </div>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs">3</span>
            </Link>
            
            <Link to="/documents?status=error" className="flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span>Error</span>
              </div>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs">1</span>
            </Link>
          </div>
        </div>
        
        <div className="px-4 py-2">
          <h2 className="mb-2 px-2 text-lg font-semibold">Categories</h2>
          <div className="space-y-1">
            <Link to="/documents?category=invoice" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <TagsIcon className="h-4 w-4" />
              <span>Invoices</span>
            </Link>
            <Link to="/documents?category=contract" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <TagsIcon className="h-4 w-4" />
              <span>Contracts</span>
            </Link>
            <Link to="/documents?category=receipt" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              <TagsIcon className="h-4 w-4" />
              <span>Receipts</span>
            </Link>
          </div>
        </div>
      </div>
      
      <div className="mt-auto px-4 py-2">
        <div className="space-y-1">
          <Link to="/settings" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </Link>
          
          <Link to="/help" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
            <HelpCircle className="h-4 w-4" />
            <span>Help & Support</span>
          </Link>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
