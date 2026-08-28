import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Task } from '../../api/tasks'

const PRIORITY_COLORS: Record<string, string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700',
}

interface Props { task: Task; isDragging?: boolean }

export default function TaskCard({ task, isDragging }: Props) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging: sd } = useSortable({ id: task.id })
  return (
    <div ref={setNodeRef} style={{ transform: CSS.Transform.toString(transform), transition, opacity: sd ? 0.4 : 1 }}
      {...attributes} {...listeners}
      className={`bg-white rounded-lg border border-gray-200 p-3 cursor-grab active:cursor-grabbing select-none
        ${isDragging ? 'shadow-lg rotate-2' : 'hover:shadow-md'} transition-shadow`}>
      <p className="text-xs text-gray-400 mb-1">#{task.taskNumber}</p>
      <p className="text-sm font-medium text-gray-900 line-clamp-2">{task.title}</p>
      <div className="flex items-center gap-2 mt-2">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${PRIORITY_COLORS[task.priority] || ''}`}>
          {task.priority}
        </span>
        {task.storyPoints && <span className="text-xs text-gray-400">{task.storyPoints} pts</span>}
      </div>
    </div>
  )
}
