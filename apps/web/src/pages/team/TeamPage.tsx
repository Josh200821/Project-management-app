import { useState } from "react"
import { useProjectAnalytics } from "../../hooks/useAnalytics"

export default function TeamPage() {
  const orgId = localStorage.getItem("currentOrgId") || ""
  const projectId = localStorage.getItem("currentProjectId") || ""
  const { data, isLoading } = useProjectAnalytics(projectId, orgId)
  const [inviteOpen, setInviteOpen] = useState(false)
  const [email, setEmail] = useState("")
  const utilization: any[] = data?.team_utilization || []

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">Team</h1>
        <button onClick={() => setInviteOpen(true)} className="px-3 py-1.5 text-xs font-medium bg-violet-600 hover:bg-violet-700 text-white rounded-lg">Invite member</button>
      </div>
      <div className="bg-slate-900/60 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              {["Member","Open tasks","Hours logged","Status"].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-slate-400 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {utilization.map((m) => (
              <tr key={m.user_id} className="border-b border-slate-800 hover:bg-slate-800/40">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center text-xs font-bold text-white">{(m.full_name||"?")[0].toUpperCase()}</div>
                    <span className="text-slate-200">{m.full_name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-slate-300">{m.open_tasks}</td>
                <td className="px-4 py-3 text-slate-300">{Number(m.hours_logged).toFixed(1)}h</td>
                <td className="px-4 py-3">
                  <span className={"inline-flex items-center px-2 py-0.5 rounded text-xs font-medium " + (m.open_tasks > 10 ? "bg-red-500/20 text-red-300" : m.open_tasks > 5 ? "bg-amber-500/20 text-amber-300" : "bg-emerald-500/20 text-emerald-300")}>
                    {m.open_tasks > 10 ? "Overloaded" : m.open_tasks > 5 ? "Busy" : "Available"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {inviteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 w-full max-w-md space-y-4">
            <h2 className="text-base font-semibold text-white">Invite team member</h2>
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="colleague@company.com"
              className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-violet-500" />
            <div className="flex gap-3 justify-end">
              <button onClick={() => setInviteOpen(false)} className="px-4 py-2 text-sm text-slate-300 hover:text-white">Cancel</button>
              <button onClick={() => setInviteOpen(false)} className="px-4 py-2 text-sm font-medium bg-violet-600 hover:bg-violet-700 text-white rounded-lg">Send invite</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}