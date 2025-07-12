import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings as SettingsIcon, Wrench } from 'lucide-react';

const Settings = () => {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-lg bg-primary/10">
            <SettingsIcon className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
            <p className="text-muted-foreground">
              Configure your application preferences and account settings
            </p>
          </div>
        </div>

        <Card className="max-w-2xl">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Wrench className="h-5 w-5 text-muted-foreground" />
              <CardTitle>Under Construction</CardTitle>
            </div>
            <CardDescription>
              We're working hard to bring you comprehensive settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                The Settings page is currently under construction. In the future, you'll be able to:
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground ml-4">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                  Configure document processing preferences
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                  Manage user account settings
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                  Set up integrations and API connections
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                  Customize notification preferences
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                  Configure security and privacy settings
                </li>
              </ul>
              <p className="text-sm text-muted-foreground mt-4">
                Check back soon for updates!
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default Settings; 