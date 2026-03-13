// Normalize task objects from various API responses to a consistent shape
export function normalizeTaskList(tasks: any[]) {
  if (!Array.isArray(tasks)) return []
  return tasks.map((t) => {
    const base = { ...t }
    base.status_name = t.status_name ?? t.status__name ?? (t.status?.name ?? '')
    base.status_code = t.status_code ?? t.status__code ?? (t.status?.code ?? '')
    return base
  })
}
