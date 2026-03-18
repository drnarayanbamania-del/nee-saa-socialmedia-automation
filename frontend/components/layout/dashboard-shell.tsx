'use client'

import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'

interface DashboardShellProps {
  children: React.ReactNode
}

export function DashboardShell({ children }: DashboardShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen">
      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-50 lg:block lg:w-72 lg:overflow-y-auto lg:bg-gray-900 lg:pb-4">
        <div className="flex h-16 items-center px-6">
          <h1 className="text-xl font-bold text-white">AI Automation Platform</h1>
        </div>
        <nav className="mt-8 px-6">
          <ul className="space-y-2">
            <li>
              <a href="/" className="flex items-center gap-3 rounded-md bg-gray-800 px-3 py-2 text-sm font-semibold text-white">
                Dashboard
              </a>
            </li>
            <li>
              <a href="/generator" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 hover:text-white">
                AI Generator
              </a>
            </li>
            <li>
              <a href="/automation" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 hover:text-white">
                Automation
              </a>
            </li>
            <li>
              <a href="/content" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 hover:text-white">
                Content Library
              </a>
            </li>
            <li>
              <a href="/publishing" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 hover:text-white">
                Publishing
              </a>
            </li>
            <li>
              <a href="/analytics" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 hover:text-white">
                Analytics
              </a>
            </li>
          </ul>
        </nav>
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetTrigger asChild className="lg:hidden">
          <Button variant="outline" size="icon" className="fixed left-4 top-4 z-50">
            <Menu className="h-4 w-4" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-72 p-0">
          <div className="flex h-16 items-center px-6">
            <h1 className="text-xl font-bold">AI Automation Platform</h1>
          </div>
          <nav className="mt-8 px-6">
            <ul className="space-y-2">
              <li>
                <a href="/" className="flex items-center gap-3 rounded-md bg-gray-100 px-3 py-2 text-sm font-semibold">
                  Dashboard
                </a>
              </li>
              <li>
                <a href="/generator" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold hover:bg-gray-100">
                  AI Generator
                </a>
              </li>
              <li>
                <a href="/automation" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold hover:bg-gray-100">
                  Automation
                </a>
              </li>
              <li>
                <a href="/content" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold hover:bg-gray-100">
                  Content Library
                </a>
              </li>
              <li>
                <a href="/publishing" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold hover:bg-gray-100">
                  Publishing
                </a>
              </li>
              <li>
                <a href="/analytics" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold hover:bg-gray-100">
                  Analytics
                </a>
              </li>
            </ul>
          </nav>
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="lg:pl-72 flex-1">
        <main className="py-8 px-6">{children}</main>
      </div>
    </div>
  )
}
