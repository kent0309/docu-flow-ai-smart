
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, ResponsiveContainer, XAxis, YAxis, Bar, Tooltip, CartesianGrid } from 'recharts';

const data = [
  { name: 'Mon', Invoices: 12, Contracts: 8, Receipts: 15 },
  { name: 'Tue', Invoices: 19, Contracts: 4, Receipts: 13 },
  { name: 'Wed', Invoices: 15, Contracts: 10, Receipts: 18 },
  { name: 'Thu', Invoices: 18, Contracts: 12, Receipts: 10 },
  { name: 'Fri', Invoices: 14, Contracts: 9, Receipts: 12 },
  { name: 'Sat', Invoices: 8, Contracts: 3, Receipts: 6 },
  { name: 'Sun', Invoices: 5, Contracts: 2, Receipts: 4 },
];

const ProcessingStats = () => {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Documents Processed</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #f0f0f0',
                borderRadius: '0.5rem',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }} 
            />
            <Bar dataKey="Invoices" fill="#0ea5e9" radius={[4, 4, 0, 0]} maxBarSize={40} />
            <Bar dataKey="Contracts" fill="#14b8a6" radius={[4, 4, 0, 0]} maxBarSize={40} />
            <Bar dataKey="Receipts" fill="#8b5cf6" radius={[4, 4, 0, 0]} maxBarSize={40} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default ProcessingStats;
