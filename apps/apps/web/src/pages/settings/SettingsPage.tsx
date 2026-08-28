import { useState } from "react"
import { useAuthStore } from "../../stores/authStore"

export default function SettingsPage() {
  const { user } = useAuthStore()
  const [fullName, setFullName] = useState(user?.full_name || "")
  const [saved, setSaved] = useState(false)

  return (
    <div className="max-w-2xl mx-auto py-8 px-4 space-y-8">
      <h1 className="text-xl font-bold text-white">Settings</h1>
      <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Profile</h2>
        <div className="flex flex-col gap-1">
          <label className="text-sm text-slate-300">Full name</label>
          <input value={fullName} onChange={(e) => setFullName(e.target.value)}
            className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-violet-500" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm text-slate-300">Email</label>
          <input value={user?.email || ""} disabled className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-600 rounded-lg text-slate-400 opacity-60" />
        </div>
        <button onClick={() => { setSaved(true); setTimeout(() => setSaved(false), 2000) }}
          className="px-4 py-2 text-sm font-medium bg-violet-600 hover:bg-violet-700 text-white rounded-lg transition-colors">
          {saved ? "Saved!" : "Save changes"}
        </button>
      </div>
      <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Security</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-200">Two-factor authentication</p>
            <p className="text-xs text-slate-400">Add extra security to your account</p>
          </div>
          <button className="px-3 py-1.5 text-xs font-medium bg-slate-700 hover:bg-slate-600 text-slate-100 border border-slate-600 rounded-md">Set up MFA</button>
        </div>
      </div>
    </div>
  )
}