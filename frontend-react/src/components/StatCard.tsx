type StatCardProps = {
  label: string
  value: number
  change: string
  accent?: 'amber' | 'teal' | 'slate' | 'rose'
}

const accentMap = {
  amber: 'bg-[#fef3c7] text-[#7c4a12]',
  teal: 'bg-[#ccfbf1] text-[#115e59]',
  slate: 'bg-[#e7e5e4] text-[#44403c]',
  rose: 'bg-[#ffe4e6] text-[#9f1239]',
}

export function StatCard({ label, value, change, accent = 'amber' }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-[0.2em] text-stone-500">{label}</p>
        <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${accentMap[accent]}`}>{change}</span>
      </div>
      <div className="mt-6 flex items-end justify-between">
        <h3 className="text-3xl font-bold text-stone-900">{value}</h3>
        <div className="h-9 w-9 rounded-xl bg-stone-100" />
      </div>
    </div>
  )
}
