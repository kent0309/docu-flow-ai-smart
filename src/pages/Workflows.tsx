
import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import WorkflowCard from '@/components/workflows/WorkflowCard';
import { Button } from '@/components/ui/button';
import { PlusCircle } from 'lucide-react';

const workflowsData = [
  {
    id: '1',
    name: 'Invoice Processing',
    description: 'Extract and validate data from invoices, then route them to the finance department',
    isActive: true,
    steps: [
      { 
        name: 'Document Classification', 
        description: 'Identify and confirm document is an invoice' 
      },
      { 
        name: 'Data Extraction', 
        description: 'Extract invoice number, date, amount, vendor details' 
      },
      { 
        name: 'Validation', 
        description: 'Validate extracted data against expected format and ranges' 
      },
      { 
        name: 'Finance System Integration', 
        description: 'Send validated invoice data to accounting system' 
      }
    ],
    documentCount: 456
  },
  {
    id: '2',
    name: 'Contract Analysis',
    description: 'Analyze contractual documents for key terms, clauses, and obligations',
    isActive: true,
    steps: [
      { 
        name: 'Document Classification', 
        description: 'Confirm document is a contract and identify contract type' 
      },
      { 
        name: 'Entity Extraction', 
        description: 'Identify parties, dates, and key entities mentioned' 
      },
      { 
        name: 'Clause Analysis', 
        description: 'Identify and categorize important contract clauses' 
      },
      { 
        name: 'Risk Assessment', 
        description: 'Analyze terms for potential risks and flag issues' 
      }
    ],
    documentCount: 148
  },
  {
    id: '3',
    name: 'Receipt Processing',
    description: 'Process expense receipts for employee reimbursement and accounting',
    isActive: false,
    steps: [
      { 
        name: 'Document Classification', 
        description: 'Verify document is a receipt' 
      },
      { 
        name: 'Data Extraction', 
        description: 'Extract merchant, date, amount, items' 
      },
      { 
        name: 'Expense Categorization', 
        description: 'Categorize expenses based on company policy' 
      },
      { 
        name: 'Expense System Integration', 
        description: 'Submit to expense management system' 
      }
    ],
    documentCount: 325
  }
];

const Workflows = () => {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
            <p className="text-muted-foreground">
              Configure automated document processing workflows
            </p>
          </div>
          <Button>
            <PlusCircle className="h-4 w-4 mr-2" />
            Create Workflow
          </Button>
        </div>

        <div className="grid gap-6 grid-cols-1">
          {workflowsData.map(workflow => (
            <WorkflowCard key={workflow.id} {...workflow} />
          ))}
        </div>
      </div>
    </MainLayout>
  );
};

export default Workflows;
