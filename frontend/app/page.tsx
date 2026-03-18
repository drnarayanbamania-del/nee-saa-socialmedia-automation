'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { DashboardShell } from '@/components/layout/dashboard-shell'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { RecentContent } from '@/components/dashboard/recent-content'
import { WorkflowBuilder } from '@/components/automation/workflow-builder'
import { ContentGenerator } from '@/components/content/content-generator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <DashboardShell>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user.username}
          </h1>
          <p className="text-muted-foreground">
            Manage your AI-powered content automation workflows
          </p>
        </div>

        <StatsCards />

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="generate">AI Generator</TabsTrigger>
            <TabsTrigger value="automate">Automation</TabsTrigger>
            <TabsTrigger value="content">Content Library</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <RecentContent />
          </TabsContent>

          <TabsContent value="generate" className="space-y-6">
            <ContentGenerator />
          </TabsContent>

          <TabsContent value="automate" className="space-y-6">
            <WorkflowBuilder />
          </TabsContent>

          <TabsContent value="content" className="space-y-6">
            <ContentLibrary />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardShell>
  )
}

// Placeholder component for Content Library
function ContentLibrary() {
  return (
    <div className="rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">Content Library</h3>
      <p className="text-muted-foreground">
        Your generated scripts, images, and videos will appear here.
      </p>
    </div>
  )
}
