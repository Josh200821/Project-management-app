import { create } from 'zustand'

export interface Task {
  id: string
  project_id: string
  task_number: number
  title: string
  description: string | null
  status: string
  priority: string
  assignee_id: string | null
  story_points: number | null
  due_date: string | null
  board_order: number
  created_at: string
  updated_at: string
}

interface TaskState {
  tasks: Record<string, Task[]>  // keyed by project_id
  board: Record<string, Task[]>  // keyed by status
  setTasks: (projectId: string, tasks: Task[]) => void
  setBoard: (board: Record<string, Task[]>) => void
  addTask: (task: Task) => void
  updateTask: (id: string, updates: Partial<Task>) => void
  removeTask: (id: string) => void
  moveTask: (taskId: string, newStatus: string, newOrder: number) => void
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: {},
  board: {},
  setTasks: (projectId, tasks) =>
    set((s) => ({ tasks: { ...s.tasks, [projectId]: tasks } })),
  setBoard: (board) => set({ board }),
  addTask: (task) =>
    set((s) => ({
      tasks: {
        ...s.tasks,
        [task.project_id]: [...(s.tasks[task.project_id] || []), task],
      },
    })),
  updateTask: (id, updates) =>
    set((s) => {
      const newBoard = { ...s.board }
      Object.keys(newBoard).forEach((status) => {
        newBoard[status] = newBoard[status].map((t) =>
          t.id === id ? { ...t, ...updates } : t
        )
      })
      return { board: newBoard }
    }),
  removeTask: (id) =>
    set((s) => {
      const newBoard = { ...s.board }
      Object.keys(newBoard).forEach((status) => {
        newBoard[status] = newBoard[status].filter((t) => t.id !== id)
      })
      return { board: newBoard }
    }),
  moveTask: (taskId, newStatus, newOrder) =>
    set((s) => {
      const newBoard = { ...s.board }
      let movedTask: Task | undefined
      Object.keys(newBoard).forEach((status) => {
        const idx = newBoard[status].findIndex((t) => t.id === taskId)
        if (idx !== -1) {
          ;[movedTask] = newBoard[status].splice(idx, 1)
        }
      })
      if (movedTask) {
        movedTask = { ...movedTask, status: newStatus, board_order: newOrder }
        newBoard[newStatus] = [...(newBoard[newStatus] || []), movedTask].sort(
          (a, b) => a.board_order - b.board_order
        )
      }
      return { board: newBoard }
    }),
}))
