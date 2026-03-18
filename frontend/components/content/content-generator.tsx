'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, Wand2, Image, Volume2, Film } from 'lucide-react'
import { api } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

export function ContentGenerator() {
  const [topic, setTopic] = useState('')
  const [tone, setTone] = useState('engaging')
  const [duration, setDuration] = useState('60')
  const [platform, setPlatform] = useState('youtube')
  const [generatedScript, setGeneratedScript] = useState<any>(null)
  const { toast } = useToast()

  const generateScript = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post('/api/v1/scripts/generate', data)
      return response.data
    },
    onSuccess: (data) => {
      setGeneratedScript(data.script)
      toast({
        title: 'Script Generated Successfully',
        description: `Generated script with ${data.script.scenes?.length || 0} scenes`,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Generation Failed',
        description: error.response?.data?.detail || 'Failed to generate script',
        variant: 'destructive',
      })
    },
  })

  const handleGenerateScript = () => {
    if (!topic.trim()) {
      toast({
        title: 'Topic Required',
        description: 'Please enter a topic to generate content about',
        variant: 'destructive',
      })
      return
    }

    generateScript.mutate({
      topic,
      tone,
      duration: parseInt(duration),
      platform,
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="h-5 w-5" />
            AI Content Generator
          </CardTitle>
          <CardDescription>
            Generate scripts, images, voiceovers, and videos from trending topics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="topic">Topic or Keyword</Label>
            <Input
              id="topic"
              placeholder="Enter a trending topic or keyword..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tone">Tone</Label>
              <Select value={tone} onValueChange={setTone}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="professional">Professional</SelectItem>
                  <SelectItem value="engaging">Engaging</SelectItem>
                  <SelectItem value="casual">Casual</SelectItem>
                  <SelectItem value="funny">Funny</SelectItem>
                  <SelectItem value="dramatic">Dramatic</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="duration">Duration (seconds)</Label>
              <Select value={duration} onValueChange={setDuration}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="30">30s (Short)</SelectItem>
                  <SelectItem value="60">60s (Standard)</SelectItem>
                  <SelectItem value="120">120s (Long)</SelectItem>
                  <SelectItem value="300">5min (Extended)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="platform">Platform</Label>
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="youtube">YouTube</SelectItem>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="tiktok">TikTok</SelectItem>
                  <SelectItem value="twitter">Twitter/X</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button
            size="lg"
            className="w-full"
            onClick={handleGenerateScript}
            disabled={generateScript.isPending}
          >
            {generateScript.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Script...
              </>
            ) : (
              <>
                <Wand2 className="mr-2 h-4 w-4" />
                Generate AI Script
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {generatedScript && (
        <Tabs defaultValue="script" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="script">
              <Wand2 className="mr-2 h-4 w-4" />
              Script
            </TabsTrigger>
            <TabsTrigger value="image">
              <Image className="mr-2 h-4 w-4" />
              Images
            </TabsTrigger>
            <TabsTrigger value="voice">
              <Volume2 className="mr-2 h-4 w-4" />
              Voice
            </TabsTrigger>
            <TabsTrigger value="video">
              <Film className="mr-2 h-4 w-4" />
              Video
            </TabsTrigger>
          </TabsList>

          <TabsContent value="script">
            <Card>
              <CardHeader>
                <CardTitle>{generatedScript.title}</CardTitle>
                <CardDescription>Generated Script Content</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Hook (First 3 seconds)</Label>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {generatedScript.hook}
                  </p>
                </div>

                <div>
                  <Label>Scenes ({generatedScript.scenes?.length || 0})</Label>
                  <div className="mt-2 space-y-3">
                    {generatedScript.scenes?.map((scene: any, index: number) => (
                      <div key={index} className="rounded-lg border p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">
                            Scene {scene.scene_number}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {scene.timestamp}
                          </span>
                        </div>
                        <p className="text-sm mb-2">{scene.narration}</p>
                        <p className="text-xs text-muted-foreground">
                          Visual: {scene.visual_description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Keywords</Label>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {generatedScript.keywords?.map((keyword: string, index: number) => (
                        <span
                          key={index}
                          className="inline-flex items-center rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label>Hashtags</Label>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {generatedScript.hashtags?.map((tag: string, index: number) => (
                        <span
                          key={index}
                          className="inline-flex items-center rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="image">
            <Card>
              <CardHeader>
                <CardTitle>AI Image Generation</CardTitle>
                <CardDescription>Generate images for each scene</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Image generation will be available after saving the script.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="voice">
            <Card>
              <CardHeader>
                <CardTitle>AI Voice Generation</CardTitle>
                <CardDescription>Convert script to realistic narration</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Voice generation will be available after saving the script.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="video">
            <Card>
              <CardHeader>
                <CardTitle>AI Video Composition</CardTitle>
                <CardDescription>Combine images, voice, and effects</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Video composition will be available after generating images and voice.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
