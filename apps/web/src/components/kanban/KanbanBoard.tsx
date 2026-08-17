import { useState } from 'react'
import { DndContext, DragEndEvent, DragOverlay, DragStartEvent, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import KanbanColumn from './KanbanColumn'
import TaskCard from './TaskCard'
import { Task } from '../../api/tasks'
import { useMoveTask } from '../../hooks/useTasks'

const COLUMNS = [
  { id: 'todo', label: 'To Do', color: 'bg-gray-100' },
  { id: 'in_progress', label: 'In Progress', color: 'bg-blue-50' },
  { id: 'in_review', label: 'In Review', color: 'bg-yellow-50' },
  { id: 'done', label: 'Done', color: 'bg-green-50' },
]

export default function KanbanBoard({ tasks, projectId }: { tasks: Task[]; projectId: string }) {
  const [activeTask, setActiveTask] = useState<Task | null>(null)
  const moveTask = useMoveTask()
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }))
  const tasksByStatus = COLUMNS.reduce(
    (acc, col) => ({ ...acc, [col.id]: tasks.filter((t) => t.status === col.id).sort((a, b) => a.boardOrder - b.boardOrder) }),
    {} as Record<string, Task[]>,
  )

  async function handleDragEnd(event: DragEndEvent) {
    setActiveTask(null)
    const { active, over } = event
    if (!over || active.id === over.id) return
    const newStatus = over.id as string
    if (COLUMNS.find((c) => c.id === newStatus)) {
      const colTasks = tasksByStatus[newStatus] || []
      const newOrder = colTasks.length ? colTasks[colTasks.length - 1].boardOrder + 1000 : 1000
      await moveTask.mutateAsync({ taskId: active.id as string, status: newStatus, boardOrder: newOrder })
    }
  }

  return (
    <DndContext sensors={sensors} onDragStart={(e: DragStartEvent) => setActiveTask(tasks.find(t => t.id === e.active.id) || null)} onDragEnd={handleDragEnd}>
      <div className="flex gap-4 overflow-x-auto pb-4 h-full">
        {COLUMNS.map((col) => <KanbanColumn key={col.id} {...col} tasks={tasksByStatus[col.id] || []} />)}
      </div>
      <DragOverlay>{activeTask ? <TaskCard task={activeTask} isDragging /> : null}</DragOverlay>
    </DndContext>
  )
}
