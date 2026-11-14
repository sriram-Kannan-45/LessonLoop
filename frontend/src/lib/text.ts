export function lessonText(value: unknown): string {
  if (Array.isArray(value)) return value.map(lessonText).join('\n')
  if (typeof value === 'object' && value !== null) return Object.values(value).map(lessonText).join('\n')
  return String(value)
}
