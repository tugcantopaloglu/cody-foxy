"use client"

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const mockTrendData = [
  { date: "Jan", critical: 12, high: 24, medium: 45, low: 67 },
  { date: "Feb", critical: 8, high: 19, medium: 38, low: 52 },
  { date: "Mar", critical: 15, high: 28, medium: 42, low: 61 },
  { date: "Apr", critical: 6, high: 15, medium: 32, low: 48 },
  { date: "May", critical: 4, high: 12, medium: 28, low: 42 },
  { date: "Jun", critical: 3, high: 8, medium: 22, low: 35 },
]

const COLORS = ["#DC2626", "#EA580C", "#F59E0B", "#22C55E"]

export function StatsChart() {
  const pieData = [
    { name: "Critical", value: 3, color: "#DC2626" },
    { name: "High", value: 8, color: "#EA580C" },
    { name: "Medium", value: 22, color: "#F59E0B" },
    { name: "Low", value: 35, color: "#22C55E" },
  ]

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Vulnerability Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockTrendData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="date" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--background))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Area type="monotone" dataKey="critical" stackId="1" stroke="#DC2626" fill="#DC2626" fillOpacity={0.6} />
                <Area type="monotone" dataKey="high" stackId="1" stroke="#EA580C" fill="#EA580C" fillOpacity={0.6} />
                <Area type="monotone" dataKey="medium" stackId="1" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.6} />
                <Area type="monotone" dataKey="low" stackId="1" stroke="#22C55E" fill="#22C55E" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Current Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--background))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-4">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-sm text-muted-foreground">{item.name}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
