
import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { ArrowRight, Settings, Play } from 'lucide-react';

interface WorkflowStep {
  name: string;
  description: string;
}

interface WorkflowCardProps {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  steps: WorkflowStep[];
  documentCount: number;
}

const WorkflowCard = ({
  id,
  name,
  description,
  isActive,
  steps,
  documentCount,
}: WorkflowCardProps) => {
  const [active, setActive] = React.useState(isActive);

  return (
    <Card className={`border-l-4 ${active ? 'border-l-primary' : 'border-l-muted'}`}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{name}</CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {active ? 'Active' : 'Inactive'}
            </span>
            <Switch checked={active} onCheckedChange={setActive} />
          </div>
        </div>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="space-y-3">
          {steps.map((step, index) => (
            <div key={index} className="flex items-start gap-2">
              <Badge variant="outline" className="mt-0.5 h-6 w-6 flex items-center justify-center p-0 font-normal rounded-full">
                {index + 1}
              </Badge>
              <div>
                <p className="font-medium text-sm">{step.name}</p>
                <p className="text-xs text-muted-foreground">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <ArrowRight className="h-4 w-4 text-muted-foreground mx-1 self-center" />
              )}
            </div>
          ))}
        </div>
      </CardContent>
      <CardFooter className="pt-2 flex justify-between">
        <div className="text-sm text-muted-foreground">
          {documentCount} document{documentCount !== 1 ? 's' : ''} processed
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-1" />
            Configure
          </Button>
          <Button size="sm">
            <Play className="h-4 w-4 mr-1" />
            Run Now
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};

export default WorkflowCard;
