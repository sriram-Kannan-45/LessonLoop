export type Provider = 'gemini' | 'openai'
export type Health = { status: 'ok'; app: string; environment: string }
export type ProviderStatus = { configured: boolean; model: string | null }
export type ProvidersStatus = Record<Provider, ProviderStatus>
export type CheckSuccess = {
  provider: Provider
  status: 'success'
  model: string
  message: string
  latency_ms: number
  checked_at: string
}
export type CheckError = {
  provider: Provider
  status: 'error'
  error_code: string
  message: string
}
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message: string, public code = 'BACKEND_UNAVAILABLE') {
    super(message)
  }
}

async function request<T>(path: string, method = 'GET'): Promise<T> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), method === 'POST' ? 125_000 : 8_000)
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { method, signal: controller.signal })
    const data: unknown = await response.json()
    if (!response.ok) {
      if (typeof data === 'object' && data !== null && 'status' in data && data.status === 'error' && 'message' in data) {
        const error = data as CheckError
        throw new ApiError(error.message, error.error_code)
      }
      throw new ApiError('The backend could not complete this request. Try again.', 'REQUEST_FAILED')
    }
    return data as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('The request timed out. Check the backend and try again.', 'TIMEOUT')
    }
    throw new ApiError('Cannot reach the backend. Start it in a separate terminal, then check again.')
  } finally {
    window.clearTimeout(timer)
  }
}

export const api = {
  health: () => request<Health>('/api/health'),
  status: () => request<ProvidersStatus>('/api/providers/status'),
  check: (provider: Provider) => request<CheckSuccess>(`/api/providers/${provider}/check`, 'POST'),
}
