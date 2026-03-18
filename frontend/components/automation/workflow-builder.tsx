'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Plus, Play, Save, Trash2 } from 'lucide-react'

export function WorkflowBuilder() {
  const [workflowName, setWorkflowName] = useState('')
  const [workflowDescription, setWorkflowDescription] = useState('')
  const [selectedTrigger, setSelectedTrigger] = useState('schedule')
  const [cronSchedule, setCronSchedule] = useState('0 */6 * * *')

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="h-5 w-5" />
            Automation Workflow Builder
          </CardTitle>
          <CardDescription>
            Create automated workflows to generate and publish content
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="workflow-name">Workflow Name</Label>
              <Input
                id="workflow-name"
                placeholder="e.g., Daily YouTube Content"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="trigger">Trigger Type</Label>
              <select
                id="trigger"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                value={selectedTrigger}
                onChange={(e) => setSelectedTrigger(e.target.value)}
              >
                <option value="schedule">Scheduled (Cron)</option>
                <option value="webhook">Webhook</option>
                <option value="manual">Manual</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Describe what this workflow does..."
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              rows={3}
            />
          </div>

          {selectedTrigger === 'schedule' && (
            <div className="space-y-2">
              <Label htmlFor="cron">Cron Schedule</Label>
              <Input
                id="cron"
                placeholder="0 */6 * * * (every 6 hours)"
                value={cronSchedule}
                onChange={(e) => setCronSchedule(e.target.value)}
              />
              <p className="text-sm text-muted-foreground">
                Every 6 hours: 0 */6 * * * | Daily at 9 AM: 0 9 * * *
              </p>
            </div>
          )}

          <div className="rounded-lg border p-4">
            <h3 className="font-semibold mb-4">Workflow Steps</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-md bg-muted p-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm">1.</span>
                  <div>
                    <p className="font-medium">Scrape Trending Topics</p>
                    <p className="text-xs text-muted-foreground">Get latest trends from YouTube, Twitter, Reddit</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center justify-between rounded-md bg-muted p-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm">2.</span>
                  <div>
                    <p className="font-medium">Generate Script</p>
                    <p className="text-xs text-muted-foreground">Create engaging script from trending topic</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center justify-between rounded-md bg-muted p-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm">3.</span>
                  <div>
                    <p className="font-medium">Generate Images</p>
                    <p className="text-xs text-muted-foreground">Create scene-based images for video</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center justify-between rounded-md bg-muted p-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm">4.</span>
                  <div>
                    <p className="font-medium">Generate Voiceover</p>
                    <p className="text-xs text-muted-foreground">Convert script to realistic narration</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center justify-between rounded-md bg-muted p-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm">5.</span>
                  <div>
                    <p className="font-medium">Compose Video</p>
                    <p className="text-xs text-muted-foreground">Combine images, voice, and effects</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center justify-between rounded-md bg-muted p-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm">6.</span>
                  <div>
                    <p className="font-medium">Publish to YouTube</p>
                    <p className="text-xs text-muted-foreground">Auto-publish with optimized title and tags</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <Button className="mt-4 w-full" variant="outline">
              <Plus className="mr-2 h-4 w-4" />
              Add Step
            </Button>
          </div>

          <div className="flex gap-4">
            <Button className="flex-1" size="lg">
              <Save className="mr-2 h-4 w-4" />
              Save Workflow
            </Button>
            <Button className="flex-1" size="lg" variant="outline">
              <Play className="mr-2 h-4 w-4" />
              Test Run
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Workflow Templates</CardTitle>
          <CardDescription>Quick-start with pre-built automation templates</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-lg border p-4 hover:bg-muted cursor-pointer">
              <h3 className="font-semibold mb-2">YouTube Shorts Factory</h3>
              <p className="text-sm text-muted-foreground">
                Auto-generate short-form content from trending topics
              </p>
            </div>
            <div className="rounded-lg border p-4 hover:bg-muted cursor-pointer">
              <h3 className="font-semibold mb-2">News Commentary</h3>
              <p className="text-sm text-muted-foreground">
                Create commentary videos from trending news articles
              </p>
            </div>
            <div className="rounded-lg border p-4 hover:bg-muted cursor-pointer">
              <h3 className="font-semibold mb-2">Educational Content</h3>
              <p className="text-sm text-muted-foreground">
                Generate explainer videos on popular topics
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
