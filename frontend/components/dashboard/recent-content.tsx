'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function RecentContent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Content</CardTitle>
        <CardDescription>Your latest generated scripts and videos</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-lg border">
            <div>
              <p className="font-medium">How AI is Changing Content Creation</p>
              <p className="text-sm text-muted-foreground">Script • 2 hours ago</p>
            </div>
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
              Completed
            </span>
          </div>
          <div className="flex items-center justify-between p-4 rounded-lg border">
            <div>
              <p className="font-medium">10 Productivity Hacks for 2024</p>
              <p className="text-sm text-muted-foreground">Video • 5 hours ago</p>
            </div>
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
              Published
            </span>
          </div>
          <div className="flex items-center justify-between p-4 rounded-lg border">
            <div>
              <p className="font-medium">The Future of Remote Work</p>
              <p className="text-sm text-muted-foreground">Script • 1 day ago</p>
            </div>
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
              Processing
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
