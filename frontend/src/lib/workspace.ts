import { API_BASE_URL, request as apiRequest } from './api'

function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  return apiRequest<T>(`/api${path}`, method, body)
}

export type Status = 'RUNNING' | 'APPROVED' | 'NEEDS_REVIEW' | 'ERROR' | 'INTERRUPTED'
export type Check = { check_id: string; passed: boolean; evidence: string; reason: string; required_change: string; claim_ids: string[]; missing_content: boolean; evidence_path?: string }
export type Lesson = {
  title: string; learning_objectives: string[]; prerequisites: string; what_it_is: string; why_it_matters: string; how_it_works: string[]
  worked_example: { context: string; learner_question: string; source_passage: string; retrieved_information: string; supported_answer: string; missing_information_question: string; missing_information_answer: string }
  limitations: string; recap: string[]; practice_questions: { question: string; answer: string }[]
  source_references: { source_id: string; claim_ids: string[] }[]
}
export type Usage = { provider?: string; model?: string; fallback?: boolean; group_usage?: Usage[]; [key: string]: unknown }
export type Attempt = { id: number; number: number; created_at: string; draft: Lesson; original_draft: Lesson | null; evaluation: Check[] | null; status: string; diagnostics: { word_count: number; sentences_over_25_words: number; note: string }; generation_usage: Usage; evaluator_usage: Usage }
export type MemoryInstruction = { id: string; topic: string; learner_profile: string; category: string; instruction: string; status: string; supporting_runs: string[]; origin: string; prompt_version: string }
export type Feedback = { id: string; category: string; message: string; status: string; review_note: string | null }
export type Run = { id: string; topic: string; learner_profile: string; status: Status; stage: string; started_at: string; finished_at: string | null; attempts: Attempt[]; attempt_count: number; final_lesson: Lesson | null; review_draft: Lesson | null; selected_memory: MemoryInstruction[]; retry_count: number; demo_error: number; generator_model: string; evaluator_model: string; generator_prompt_version: string; source_pack_version: string; rubric_version: string; error: { code: string; message: string; diagnostics?: { provider?: string; provider_http_status?: number; retry_after_seconds?: number } } | null; feedback: Feedback[] }
export type RunSummary = Pick<Run, 'id' | 'topic' | 'status' | 'stage' | 'started_at' | 'attempt_count'>
export type Event = { sequence: number; stage: string; message: string; created_at: string; details: Record<string, unknown> }
export type Source = { id: string; title: string; url: string; accessed_at: string; version?: string; license?: string; license_url?: string; notes: { id: string; text: string; claim_ids: string[] }[] }
export type RubricCheck = { id: string; name: string; group: string; pass: string; fail: string; evidence: string; evaluator: string; mandatory: boolean }
export type Workspace = { source_pack: { id: string; version: string; sources: Source[]; review_note: string }; rubric: { version: string; checks: RubricCheck[] }; learner_profile: string; generator_model: string; evaluator_model: string; provider_note: string; evaluation_groups: number; technical_retries: number; fallback?: { enabled: boolean; configured: boolean; provider: string; generator_model: string; evaluator_model: string; min_interval_seconds: number }; configured: boolean; busy: boolean; active_prompt_version: string; improvement_categories: string[]; demo_enabled: boolean }
export type ComparisonArm = { prompt_version: string; draft: Lesson; checks: Check[]; approved: boolean }
export type Experiment = { id: string; category: string; status: string; stage: string; baseline_prompt_version: string; candidate_prompt_version: string; memory_id: string; created_at: string; results: { case_id: string; baseline?: ComparisonArm; candidate?: ComparisonArm; regressions?: string[]; fixed_checks?: string[]; target_improved?: boolean; provider_comparison_valid?: boolean }[]; error: { code: string; message: string } | null }
export type PromptVersion = { version: string; active: number; parent: string | null; instructions: string; memory_ids: string[] }
export type Memory = { instructions: MemoryInstruction[]; failure_categories: { category: string; independent_runs: number }[]; prompt_versions: PromptVersion[]; experiments: Experiment[]; active_prompt_version: string }
export type FrozenRun = Run & { source_snapshot?: { sources: Source[] }; rubric_snapshot?: { version: string; checks: RubricCheck[] } }

export const workspaceApi = {
  workspace: () => request<Workspace>('/workspace'),
  create: (topic: string, demo_error: boolean) => request<{ id: string; status: Status }>('/runs', 'POST', { topic, learner_profile: 'india_beginner', reference_pack_id: 'auto', demo_error }),
  run: (id: string) => request<FrozenRun>(`/runs/${id}`),
  history: (offset = 0) => request<{ items: RunSummary[]; total: number; limit: number; offset: number }>(`/runs?limit=10&offset=${offset}`),
  events: (id: string, after = 0) => request<{ events: Event[]; next_cursor: number }>(`/runs/${id}/events?after=${after}`),
  feedback: (id: string, category: string, message: string) => request<{ id: string; status: string; message: string }>(`/runs/${id}/feedback`, 'POST', { category, message }),
  reviewFeedback: (id: string, action: string, review_note: string) => request(`/feedback/${id}/review`, 'POST', { action, review_note }),
  memory: () => request<Memory>('/memory'),
  improve: (category: string) => request<{ id: string; status: string }>('/improvements', 'POST', { category }),
  experiment: (id: string) => request<Experiment>(`/improvements/${id}`),
  rollback: (prompt_version: string) => request('/prompts/rollback', 'POST', { prompt_version }),
  exportUrl: (id: string, format: 'json' | 'markdown') => `${API_BASE_URL}/api/runs/${id}/export?format=${format}`,
}
