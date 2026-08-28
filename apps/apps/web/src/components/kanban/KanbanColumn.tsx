import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import TaskCard from './TaskCard'
import { Task } from '../../api/tasks'

interface Props { id: string; label: string; color: string; tasks: Task[] }

export default function KanbanColumn({ id, label, color, tasks }: Props) {
  const { setNodeRef, isOver } = useDroppable({ id })
  return (
    <div className={`flex flex-col w-72 shrink-0 rounded-xl ${color} ${isOver ? 'ring-2 ring-primary-400' : ''}`}>
      <div className="p-3 font-medium text-sm text-gray-700 flex items-center justify-between">
        <span>{label}</span>
        <span className="bg-white text-gray-500 text-xs px-2 py-0.5 rounded-full border">{tasks.length}</span>
      </div>
      <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
        <div ref={setNodeRef} className="flex-1 p-2 space-y-2 min-h-48">
          {tasks.map((task) => <TaskCard key={task.id} task={task} />)}
        </div>
      </SortableContext>
    </div>
  )
}
