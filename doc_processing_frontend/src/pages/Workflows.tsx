import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import WorkflowCard from '@/components/workflows/WorkflowCard';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { PlusCircle, Trash2 } from 'lucide-react';
import { fetchWorkflows, createWorkflow, createWorkflowStep } from '@/lib/api'; 
import { useToast } from '@/components/ui/use-toast';

const Workflows = () => {
  const [workflows, setWorkflows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    steps: [{ name: '', description: '', step_order: 1 }]
  });
  const { toast } = useToast();

  useEffect(() => {
    // Fetch workflows from API
    const getWorkflows = async () => {
      try {
        const response = await fetchWorkflows();
        setWorkflows(response);
      } catch (error) {
        console.error('Error fetching workflows:', error);
        toast({
          title: 'Error',
          description: 'Failed to load workflows.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    getWorkflows();
  }, [toast]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewWorkflow(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleStepChange = (index, e) => {
    const { name, value } = e.target;
    const updatedSteps = [...newWorkflow.steps];
    updatedSteps[index] = { ...updatedSteps[index], [name]: value, step_order: index + 1 };
    
    setNewWorkflow(prev => ({
      ...prev,
      steps: updatedSteps
    }));
  };

  const addStep = () => {
    setNewWorkflow(prev => ({
      ...prev,
      steps: [
        ...prev.steps,
        { name: '', description: '', step_order: prev.steps.length + 1 }
      ]
    }));
  };

  const removeStep = (index) => {
    const updatedSteps = [...newWorkflow.steps];
    updatedSteps.splice(index, 1);
    
    // Update step_order for remaining steps
    const reorderedSteps = updatedSteps.map((step, idx) => ({
      ...step,
      step_order: idx + 1
    }));
    
    setNewWorkflow(prev => ({
      ...prev,
      steps: reorderedSteps
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsLoading(true);
      
      // First create the workflow
      const workflowResponse = await createWorkflow({
        name: newWorkflow.name,
        description: newWorkflow.description,
        is_active: true
      });
      
      const workflowId = workflowResponse.id;
      
      // Then create each step
      const stepPromises = newWorkflow.steps.map(step => 
        createWorkflowStep({
          workflow: workflowId,
          name: step.name,
          description: step.description,
          step_order: step.step_order
        })
      );
      
      await Promise.all(stepPromises);
      
      // Refresh the workflows list
      const response = await fetchWorkflows();
      setWorkflows(response);
      
      // Close modal and reset form
      setIsModalOpen(false);
      setNewWorkflow({
        name: '',
        description: '',
        steps: [{ name: '', description: '', step_order: 1 }]
      });
      
      toast({
        title: 'Success',
        description: 'Workflow created successfully.',
      });
    } catch (error) {
      console.error('Error creating workflow:', error);
      toast({
        title: 'Error',
        description: 'Failed to create workflow.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

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
          <Button onClick={() => setIsModalOpen(true)}>
            <PlusCircle className="h-4 w-4 mr-2" />
            Create Workflow
          </Button>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <p>Loading workflows...</p>
          </div>
        ) : (
          <div className="grid gap-6 grid-cols-1">
            {workflows.length > 0 ? (
              workflows.map(workflow => (
                <WorkflowCard key={workflow.id} {...workflow} />
              ))
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No workflows found. Create your first workflow to get started.</p>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Create Workflow Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>Create New Workflow</DialogTitle>
            <DialogDescription>
              Define a new document processing workflow. Add the steps needed to process your documents.
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-6 py-4">
            <div className="grid gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Workflow Name</Label>
                <Input 
                  id="name" 
                  name="name" 
                  value={newWorkflow.name} 
                  onChange={handleInputChange} 
                  placeholder="e.g., Invoice Processing" 
                  required 
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea 
                  id="description" 
                  name="description" 
                  value={newWorkflow.description} 
                  onChange={handleInputChange} 
                  placeholder="Describe what this workflow does" 
                  required 
                />
              </div>
              
              <div className="space-y-4 pt-4">
                <div className="flex items-center justify-between">
                  <Label className="text-lg">Workflow Steps</Label>
                  <Button type="button" variant="outline" onClick={addStep}>
                    <PlusCircle className="h-4 w-4 mr-2" />
                    Add Step
                  </Button>
                </div>
                
                {newWorkflow.steps.map((step, index) => (
                  <div key={index} className="border p-4 rounded-md space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="font-semibold">Step {index + 1}</h3>
                      {newWorkflow.steps.length > 1 && (
                        <Button 
                          type="button" 
                          variant="destructive" 
                          size="sm" 
                          onClick={() => removeStep(index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor={`step-name-${index}`}>Name</Label>
                      <Input 
                        id={`step-name-${index}`} 
                        name="name" 
                        value={step.name} 
                        onChange={(e) => handleStepChange(index, e)} 
                        placeholder="e.g., Document Classification" 
                        required 
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor={`step-desc-${index}`}>Description</Label>
                      <Textarea 
                        id={`step-desc-${index}`} 
                        name="description" 
                        value={step.description} 
                        onChange={(e) => handleStepChange(index, e)} 
                        placeholder="What happens in this step" 
                        required 
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setIsModalOpen(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Workflow'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </MainLayout>
  );
};

export default Workflows;
