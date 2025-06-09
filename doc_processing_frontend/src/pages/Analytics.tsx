import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  LineChart, 
  BarChart, 
  PieChart, 
  Pie,
  Line, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Cell
} from 'recharts';

const monthlyData = [
  { name: 'Jan', invoices: 65, contracts: 28, receipts: 40, reports: 15 },
  { name: 'Feb', invoices: 59, contracts: 35, receipts: 37, reports: 18 },
  { name: 'Mar', invoices: 80, contracts: 30, receipts: 50, reports: 20 },
  { name: 'Apr', invoices: 81, contracts: 45, receipts: 60, reports: 17 },
  { name: 'May', invoices: 56, contracts: 36, receipts: 45, reports: 22 },
];

const accuracyData = [
  { name: 'Jan', accuracy: 92 },
  { name: 'Feb', accuracy: 93 },
  { name: 'Mar', accuracy: 94 },
  { name: 'Apr', accuracy: 95 },
  { name: 'May', accuracy: 97 },
];

const processingTimeData = [
  { name: 'Jan', time: 45 },
  { name: 'Feb', time: 40 },
  { name: 'Mar', time: 38 },
  { name: 'Apr', time: 30 },
  { name: 'May', time: 25 },
];

const documentTypeData = [
  { name: 'Invoices', value: 341, color: '#0ea5e9' },
  { name: 'Contracts', value: 174, color: '#14b8a6' },
  { name: 'Receipts', value: 232, color: '#8b5cf6' },
  { name: 'Reports', value: 92, color: '#f59e0b' },
  { name: 'Other', value: 39, color: '#64748b' },
];

const topErrorsData = [
  { name: 'Missing Invoice Number', count: 15 },
  { name: 'Unreadable Date', count: 12 },
  { name: 'Invalid Amount Format', count: 9 },
  { name: 'Unknown Vendor', count: 7 },
  { name: 'Duplicate Detection', count: 5 },
];

const Analytics = () => {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Insights and performance metrics for your document processing
          </p>
        </div>

        <Tabs defaultValue="performance">
          <TabsList>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="errors">Errors</TabsTrigger>
          </TabsList>
          
          <TabsContent value="performance" className="pt-6 space-y-6">
            <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Processing Accuracy</CardTitle>
                  <CardDescription>
                    AI processing accuracy over time
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={accuracyData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" />
                      <YAxis domain={[90, 100]} />
                      <Tooltip />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="accuracy" 
                        name="Accuracy (%)" 
                        stroke="#0ea5e9" 
                        activeDot={{ r: 8 }}
                        strokeWidth={3}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Average Processing Time</CardTitle>
                  <CardDescription>
                    Average time to process documents (seconds)
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={processingTimeData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="time" 
                        name="Processing Time (sec)" 
                        stroke="#14b8a6" 
                        activeDot={{ r: 8 }} 
                        strokeWidth={3}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="documents" className="pt-6 space-y-6">
            <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Documents Processed by Type</CardTitle>
                  <CardDescription>
                    Distribution of document types processed
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={documentTypeData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {documentTypeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`${value} documents`, 'Count']} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Monthly Document Processing</CardTitle>
                  <CardDescription>
                    Number of documents processed by month and type
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={monthlyData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="invoices" name="Invoices" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="contracts" name="Contracts" fill="#14b8a6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="receipts" name="Receipts" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="reports" name="Reports" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="errors" className="pt-6 space-y-6">
            <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Top Error Categories</CardTitle>
                  <CardDescription>
                    Most common errors encountered during processing
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart 
                      data={topErrorsData}
                      layout="vertical"
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                      <XAxis type="number" />
                      <YAxis dataKey="name" type="category" width={150} />
                      <Tooltip />
                      <Bar dataKey="count" name="Occurrences" fill="#ef4444" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Error Rate by Document Type</CardTitle>
                  <CardDescription>
                    Percentage of documents with processing errors
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center h-80">
                  <div className="grid grid-cols-2 gap-6 w-full">
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium">Invoices</p>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-muted rounded-full h-2.5">
                            <div className="bg-primary h-2.5 rounded-full" style={{ width: '3.2%' }}></div>
                          </div>
                          <span className="text-sm">3.2%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Contracts</p>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-muted rounded-full h-2.5">
                            <div className="bg-teal-500 h-2.5 rounded-full" style={{ width: '4.8%' }}></div>
                          </div>
                          <span className="text-sm">4.8%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Receipts</p>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-muted rounded-full h-2.5">
                            <div className="bg-purple-500 h-2.5 rounded-full" style={{ width: '2.5%' }}></div>
                          </div>
                          <span className="text-sm">2.5%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Reports</p>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-muted rounded-full h-2.5">
                            <div className="bg-amber-500 h-2.5 rounded-full" style={{ width: '1.7%' }}></div>
                          </div>
                          <span className="text-sm">1.7%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Other</p>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-muted rounded-full h-2.5">
                            <div className="bg-slate-500 h-2.5 rounded-full" style={{ width: '5.3%' }}></div>
                          </div>
                          <span className="text-sm">5.3%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-4xl font-bold text-primary mb-2">3.1%</div>
                        <p className="text-sm text-muted-foreground">Average Error Rate</p>
                        <p className="text-xs text-green-500 font-medium mt-3">↓ 0.8% from last month</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
};

export default Analytics;
