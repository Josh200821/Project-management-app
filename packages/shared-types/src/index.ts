/**
 * Shared TypeScript types for the SaaS Platform.
 * Generated from OpenAPI spec — do not edit manually.
 */

export interface ApiResponse<T> {
  data: T
  meta?: {
    total?: number
    page?: number
    per_page?: number
    pages?: number
  }
  errors: string[]
}

export interface User {
  id: string
  email: string
  full_name: string | null
  avatar_url: string | null
  mfa_enabled: boolean
  is_active: boolean
  created_at: string
}

export interface Organization {
  id: string
  name: string
  slug: string
  logo_url: string | null
  plan: "free" | "pro" | "enterprise"
  created_at: string
}

export interface Project {
  id: string
  organization_id: string
  name: string
  slug: string
  description: string | null
  status: "active" | "archived" | "deleted"
  task_counter: number
  created_at: string
  updated_at: string
}

export type TaskStatus = "todo" | "in_progress" | "in_review" | "done" | "cancelled"
export type TaskPriority = "critical" | "high" | "medium" | "low"

export interface Task {
  id: string
  project_id: string
  task_number: number
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  story_points: number | null
  due_date: string | null
  assignee_id: string | null
  created_by: string | null
  board_order: number
  sprint_id: string | null
  created_at: string
  updated_at: string
}

export interface Sprint {
  id: string
  project_id: string
  name: string
  goal: string | null
  start_date: string | null
  end_date: string | null
  status: "planning" | "active" | "closed"
  capacity_points: number | null
  velocity_points: number | null
  created_at: string
}

export interface Comment {
  id: string
  task_id: string
  author_id: string
  body: string
  edited_at: string | null
  created_at: string
}

export interface Notification {
  id: string
  type: string
  title: string
  body: string
  entity_type: string | null
  entity_id: string | null
  read_at: string | null
  created_at: string
}

export interface Webhook {
  id: string
  url: string
  events: string[]
  is_active: boolean
  failure_count: number
  last_success_at: string | null
  created_at: string
}

export interface ProjectAnalytics {
  total_tasks: number
  completed_tasks: number
  open_tasks: number
  overdue_tasks: number
  velocity: Array<{ sprint_name: string; completed_points: number; planned_points: number }>
  status_distribution: Array<{ status: string; count: number }>
  team_utilization: Array<{ user_id: string; full_name: string; open_tasks: number; hours_logged: number }>
}
