// Shared types mirroring the FastAPI backend response shapes exactly.

export type Classification = "Automate" | "Augment" | "Human-led"
export type Priority = "High" | "Medium" | "Low"

export interface Organization {
  id: number
  name: string
  industry: string
  description: string
  is_fictional: number
}

export interface Role {
  id: number
  organization_id: number
  name: string
  department: string | null
  seniority: string | null
  description: string | null
  is_ai_generated: number
  created_at?: string
}

export interface Skill {
  id: number
  name: string
  category: string
  description?: string | null
}

export interface Activity {
  id: number
  process_id: number
  name: string
  description: string | null
  time_share: number
  repetitiveness: number
  rule_based: number
  data_availability: number
  decision_complexity: number
  human_interaction: number
  skills: Skill[]
}

export interface Process {
  id: number
  name: string
  description: string | null
  activities: Activity[]
}

export interface RoleGraph extends Role {
  processes: Process[]
}

export type FutureResponsibility =
  | string
  | {
      title: string
      description?: string
    }

export type FutureSkill =
  | string
  | {
      skill: string
      reason?: string
    }

export interface Profile {
  overall_impact: number
  automation_pct: number
  augmentation_pct: number
  human_pct: number
  reskilling_priority: Priority
  reskilling_index: number
  future_responsibilities: FutureResponsibility[]
  future_skills: FutureSkill[]
  narrative: string | null
  source: "ai" | "fallback"
}

export type CapabilityItem =
  | string
  | {
      name: string
      relevance?: number
    }

export interface ActivityResult {
  activity_id: number
  name: string
  time_share: number
  impact: number
  classification: Classification
  signals: Record<string, number>
  contributions: Record<string, number>
  factors: Record<string, number>
  process: { process_id?: number; process_name?: string }
  rationale: string
  ai_capabilities: CapabilityItem[]
  assessment_source: "ai" | "fallback"
}

export interface Methodology {
  weights: Record<string, number>
  thresholds: { automate: number; augment: number }
  signal_definitions: Record<string, string>
  formula: string
}

export interface Evidence {
  id: number
  source: string
  title: string
  url: string
  year: number
  tag: string
  summary: string
}

export interface AnalysisResult {
  role: Role
  profile: Profile
  activities: ActivityResult[]
  methodology: Methodology
  evidence: Evidence[]
  ai_available: boolean
  from_cache: boolean
}

export interface DashboardResponse {
  organization: Organization | null
  stats: {
    total_roles: number
    total_activities: number
    analyzed_roles: number
  }
  departments: string[]
  ai_available: boolean
}

export interface RolesResponse {
  roles: Role[]
}

export interface RoleDetailResponse {
  role: RoleGraph
  profile: Profile | null
}
