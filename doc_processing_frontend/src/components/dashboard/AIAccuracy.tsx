
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, ResponsiveContainer, XAxis, YAxis, Line, Tooltip, CartesianGrid } from 'recharts';

const data = [
  { name: 'Week 1', accuracy: 91 },
  { name: 'Week 2', accuracy: 94 },
  { name: 'Week 3', accuracy: 93 },
  { name: 'Week 4', accuracy: 95 },
  { name: 'Week 5', accuracy: 97 },
  { name: 'Week 6', accuracy: 96 },
  { name: 'Week 7', accuracy: 98 },
];

const AIAccuracy = () => {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>AI Processing Accuracy</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis dataKey="name" />
            <YAxis domain={[85, 100]} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #f0f0f0',
                borderRadius: '0.5rem',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }} 
              formatter={(value) => [`${value}%`, 'Accuracy']}
            />
            <Line 
              type="monotone" 
              dataKey="accuracy" 
              stroke="#0ea5e9" 
              strokeWidth={3} 
              dot={{ r: 4, strokeWidth: 2 }} 
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default AIAccuracy;
