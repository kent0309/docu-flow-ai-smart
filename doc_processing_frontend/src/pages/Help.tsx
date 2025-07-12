import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { HelpCircle, BookOpen, MessageCircle, Mail } from 'lucide-react';

const Help = () => {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-lg bg-blue-500/10">
            <HelpCircle className="h-8 w-8 text-blue-500" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Help & Support</h1>
            <p className="text-muted-foreground">
              Get assistance and learn how to make the most of your document processing
            </p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <BookOpen className="h-5 w-5 text-blue-500" />
                <CardTitle className="text-lg">Documentation</CardTitle>
              </div>
              <CardDescription>
                Comprehensive guides and tutorials
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Detailed documentation covering all features, API references, and best practices will be available here soon.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <MessageCircle className="h-5 w-5 text-green-500" />
                <CardTitle className="text-lg">Community Support</CardTitle>
              </div>
              <CardDescription>
                Connect with other users
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Join our community forums to ask questions, share tips, and get help from other users.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-purple-500" />
                <CardTitle className="text-lg">Contact Support</CardTitle>
              </div>
              <CardDescription>
                Direct assistance from our team
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Reach out to our support team for technical assistance and personalized help.
              </p>
            </CardContent>
          </Card>
        </div>

        <Card className="max-w-3xl">
          <CardHeader>
            <CardTitle>Coming Soon</CardTitle>
            <CardDescription>
              Help and support resources will be available here soon
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                We're building comprehensive help resources to make your experience as smooth as possible. Soon you'll find:
              </p>
              <div className="grid gap-3 md:grid-cols-2">
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Getting Started</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground ml-4">
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                      Quick start guide
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                      Video tutorials
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                      Feature walkthroughs
                    </li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Advanced Topics</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground ml-4">
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                      API documentation
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                      Integration guides
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50" />
                      Troubleshooting tips
                    </li>
                  </ul>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mt-4">
                In the meantime, feel free to explore the application and reach out if you need assistance!
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default Help; 