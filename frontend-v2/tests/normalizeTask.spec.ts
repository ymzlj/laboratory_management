import { describe, it, expect } from 'vitest'
import { normalizeTaskList } from '../src/utils/normalizeTask'

describe('normalizeTaskList', () => {
  it('maps status__name and status__code to status_name and status_code', () => {
    const input = [
      { id: 1, task_number: 'T1', task_name: 'Task 1', status__name: 'Pending', status__code: 'pending' },
      { id: 2, task_number: 'T2', task_name: 'Task 2', status: { name: 'In Progress', code: 'in_progress' } },
    ] as any[]

    const out = normalizeTaskList(input)
    expect(out[0].status_name).toBe('Pending')
    expect(out[0].status_code).toBe('pending')
    expect(out[1].status_name).toBe('In Progress')
    expect(out[1].status_code).toBe('in_progress')
  })
})
