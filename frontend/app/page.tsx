"use client"

import { useEffect, useMemo, useState, type ReactNode } from "react"
import { api, ApiError } from "@/lib/api"
import type { AnalysisResult, DashboardResponse, Role } from "@/lib/types"

const emptyForm = { name: "", department: "", description: "" }

function normalizeResponsibility(item: string | { title: string; description?: string }) {
  if (typeof item === "string") {
    return { title: item, description: "" }
  }
  return { title: item.title || "Responsibility", description: item.description || "" }
}

function normalizeSkill(item: string | { skill: string; reason?: string }) {
  if (typeof item === "string") {
    return { skill: item, reason: "" }
  }
  return { skill: item.skill || "Skill", reason: item.reason || "" }
}

function normalizeCapability(item: string | { name: string; relevance?: number }) {
  if (typeof item === "string") {
    return item
  }
  return item.name || "AI capability"
}

export default function Page() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [roles, setRoles] = useState<Role[]>([])
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null)
  const [compareLeft, setCompareLeft] = useState<number | null>(null)
  const [compareRight, setCompareRight] = useState<number | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [compareResult, setCompareResult] = useState<{ a: AnalysisResult; b: AnalysisResult } | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [busyRoleId, setBusyRoleId] = useState<number | null>(null)

  const selectedRole = useMemo(
    () => roles.find((role) => role.id === selectedRoleId) ?? null,
    [roles, selectedRoleId],
  )

  const syncInitialSelection = async () => {
    const dashboardData = await api.dashboard()
    setDashboard(dashboardData)
    const roleData = await api.listRoles()
    setRoles(roleData.roles)
    if (roleData.roles[0]) {
      setSelectedRoleId(roleData.roles[0].id)
      setCompareLeft(roleData.roles[0].id)
      setCompareRight(roleData.roles[1]?.id ?? roleData.roles[0].id)
    }
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      try {
        await syncInitialSelection()
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Could not load project data")
      } finally {
        setLoading(false)
      }
    }
    void init()
  }, [])

  useEffect(() => {
    if (!selectedRoleId) return
    const fetchRoleAnalysis = async () => {
      try {
        const detail = await api.getRole(selectedRoleId)
        if (!detail.role) return
        try {
          const analyzed = await api.analyzeRole(selectedRoleId)
          setAnalysis(analyzed)
        } catch {
          setAnalysis(null)
        }
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Role could not be loaded")
      }
    }
    void fetchRoleAnalysis()
  }, [selectedRoleId])

  const handleAnalyze = async (roleId: number) => {
    setBusyRoleId(roleId)
    setError(null)
    try {
      const result = await api.analyzeRole(roleId, true)
      setAnalysis(result)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Analysis failed")
    } finally {
      setBusyRoleId(null)
    }
  }

  const handleCompare = async () => {
    if (compareLeft == null || compareRight == null || compareLeft === compareRight) {
      setError("Please select two different roles to compare")
      return
    }
    try {
      const result = await api.compare(compareLeft, compareRight)
      setCompareResult(result)
      setError(null)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Comparison failed")
    }
  }

  const handleCreateRole = async () => {
    if (!form.name.trim()) {
      setError("Role name is required")
      return
    }
    try {
      const result = await api.createRole({
        name: form.name,
        department: form.department || undefined,
        description: form.description || undefined,
      })
      setForm(emptyForm)
      await syncInitialSelection()
      setSelectedRoleId(result.role_id)
      setAnalysis(result.analysis)
      setError(null)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create role")
    }
  }

  return (
    <main className="min-h-screen bg-[#0b1020] text-slate-100">
      <div className="mx-auto max-w-7xl p-6">
        <header className="mb-8 flex flex-col gap-4 border-b border-slate-800 pb-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.28rem] text-violet-300">Modus Enterprise AI Build Challenge</p>
            <h1 className="mt-2 text-3xl font-bold text-white">Role-Level AI Intelligence</h1>
          </div>
          <div className="rounded-xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-sm text-slate-300">
            <div className="font-medium text-slate-100">{dashboard?.organization?.name ?? "Meridian Financial Group"}</div>
            <div>{dashboard?.organization?.industry ?? "Banking & Financial Services"}</div>
          </div>
        </header>

        {error ? (
          <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        {!loading && dashboard ? (
          <section className="mb-8 grid gap-4 md:grid-cols-4">
            <StatCard label="Total roles" value={dashboard.stats.total_roles} />
            <StatCard label="Activities" value={dashboard.stats.total_activities} />
            <StatCard label="Analyzed" value={dashboard.stats.analyzed_roles} />
            <StatCard label="AI available" value={dashboard.ai_available ? "Yes" : "No"} />
          </section>
        ) : null}

        <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
          <aside className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
              <h2 className="mb-3 text-lg font-semibold">Role list</h2>
              <div className="space-y-2">
                {roles.map((role) => (
                  <button
                    key={role.id}
                    type="button"
                    onClick={() => setSelectedRoleId(role.id)}
                    className={`w-full rounded-xl border px-3 py-2 text-left transition ${
                      selectedRoleId === role.id
                        ? "border-violet-500 bg-violet-500/10 text-white"
                        : "border-slate-700 bg-slate-950/60 text-slate-300 hover:border-slate-500"
                    }`}
                  >
                    <div className="font-medium">{role.name}</div>
                    <div className="text-xs text-slate-400">{role.department ?? "General"}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
              <h2 className="mb-3 text-lg font-semibold">Add new role</h2>
              <div className="space-y-3">
                <input
                  value={form.name}
                  onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                  placeholder="Role name"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none ring-0 placeholder:text-slate-500"
                />
                <input
                  value={form.department}
                  onChange={(e) => setForm((prev) => ({ ...prev, department: e.target.value }))}
                  placeholder="Department"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none ring-0 placeholder:text-slate-500"
                />
                <textarea
                  value={form.description}
                  onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
                  placeholder="Role description"
                  rows={4}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none ring-0 placeholder:text-slate-500"
                />
                <button
                  type="button"
                  onClick={handleCreateRole}
                  className="w-full rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-500"
                >
                  Create & analyze
                </button>
              </div>
            </div>
          </aside>

          <section className="space-y-6">
            {selectedRole ? (
              <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
                <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.25rem] text-slate-400">Selected role</p>
                    <h2 className="mt-2 text-2xl font-bold text-white">{selectedRole.name}</h2>
                    <p className="mt-1 text-sm text-slate-400">{selectedRole.department ?? "General"} • {selectedRole.seniority ?? "Mid"}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleAnalyze(selectedRole.id)}
                    className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-60"
                    disabled={busyRoleId === selectedRole.id}
                  >
                    {busyRoleId === selectedRole.id ? "Analyzing..." : "Analyze role"}
                  </button>
                </div>

                <div className="mb-6 grid gap-4 md:grid-cols-3">
                  <MetricCard label="Overall AI impact" value={analysis?.profile?.overall_impact ?? 0} suffix="%" tone="violet" />
                  <MetricCard label="Automation" value={analysis?.profile?.automation_pct ?? 0} suffix="%" tone="cyan" />
                  <MetricCard label="Augmentation" value={analysis?.profile?.augmentation_pct ?? 0} suffix="%" tone="amber" />
                </div>

                {analysis?.profile ? (
                  <div className="mb-6 grid gap-4 lg:grid-cols-[1.4fr_0.6fr]">
                    <div className="rounded-xl border border-slate-700 bg-slate-950/70 p-4">
                      <h3 className="mb-2 text-sm font-semibold uppercase tracking-[0.2rem] text-slate-400">Future role narrative</h3>
                      <p className="text-sm leading-6 text-slate-300">{analysis.profile.narrative ?? "No narrative yet."}</p>
                    </div>
                    <div className="rounded-xl border border-slate-700 bg-slate-950/70 p-4">
                      <h3 className="mb-2 text-sm font-semibold uppercase tracking-[0.2rem] text-slate-400">Reskilling</h3>
                      <div className="text-xl font-bold text-white">{analysis.profile.reskilling_priority}</div>
                      <div className="mt-2 text-sm text-slate-300">Index: {analysis.profile.reskilling_index}</div>
                    </div>
                  </div>
                ) : null}

                {analysis?.profile?.future_responsibilities?.length ? (
                  <div className="mb-6 grid gap-4 md:grid-cols-2">
                    <Panel title="Future responsibilities">
                      <ul className="space-y-3 text-sm text-slate-300">
                        {analysis.profile.future_responsibilities.map((item, index) => {
                          const normalized = normalizeResponsibility(item)
                          return (
                            <li key={`${normalized.title}-${index}`} className="rounded-lg border border-slate-700 bg-slate-950/60 p-3">
                              <div className="font-medium text-white">{normalized.title}</div>
                              {normalized.description ? <div className="mt-1 text-slate-400">{normalized.description}</div> : null}
                            </li>
                          )
                        })}
                      </ul>
                    </Panel>

                    <Panel title="Future skills">
                      <ul className="space-y-3 text-sm text-slate-300">
                        {analysis.profile.future_skills.map((item, index) => {
                          const normalized = normalizeSkill(item)
                          return (
                            <li key={`${normalized.skill}-${index}`} className="rounded-lg border border-slate-700 bg-slate-950/60 p-3">
                              <div className="font-medium text-white">{normalized.skill}</div>
                              {normalized.reason ? <div className="mt-1 text-slate-400">{normalized.reason}</div> : null}
                            </li>
                          )
                        })}
                      </ul>
                    </Panel>
                  </div>
                ) : null}

                {analysis?.activities?.length ? (
                  <div className="mb-6">
                    <h3 className="mb-3 text-lg font-semibold">Activity exposure</h3>
                    <div className="space-y-3">
                      {analysis.activities.map((activity) => (
                        <div key={activity.activity_id} className="rounded-xl border border-slate-700 bg-slate-950/60 p-4">
                          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                            <div>
                              <div className="font-medium text-white">{activity.name}</div>
                              <div className="text-xs text-slate-400">{activity.process?.process_name ?? "General process"}</div>
                            </div>
                            <div className="rounded-full border border-slate-600 bg-slate-900 px-2 py-1 text-xs font-medium text-slate-200">
                              {activity.classification} • {activity.impact}
                            </div>
                          </div>
                          <p className="mt-2 text-sm text-slate-300">{activity.rationale}</p>
                          <div className="mt-3 flex flex-wrap gap-2">
                            {activity.ai_capabilities?.map((capability, idx) => {
                              const name = normalizeCapability(capability)
                              return (
                                <span key={`${name}-${idx}`} className="rounded-full bg-violet-500/10 px-2 py-1 text-xs text-violet-200">
                                  {name}
                                </span>
                              )
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {analysis?.evidence?.length ? (
                  <Panel title="Evidence and research">
                    <ul className="space-y-3 text-sm text-slate-300">
                      {analysis.evidence.slice(0, 4).map((item) => (
                        <li key={item.id} className="rounded-lg border border-slate-700 bg-slate-950/60 p-3">
                          <div className="font-medium text-white">{item.title}</div>
                          <div className="mt-1 text-xs text-violet-200">{item.source} • {item.year}</div>
                          <div className="mt-2 text-slate-400">{item.summary}</div>
                        </li>
                      ))}
                    </ul>
                  </Panel>
                ) : null}
              </div>
            ) : (
              <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 text-slate-300">
                Select a role to start analyzing.
              </div>
            )}

            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
              <h3 className="mb-4 text-lg font-semibold">Compare roles</h3>
              <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
                <select
                  value={compareLeft ?? ""}
                  onChange={(e) => setCompareLeft(Number(e.target.value))}
                  className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                >
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
                <select
                  value={compareRight ?? ""}
                  onChange={(e) => setCompareRight(Number(e.target.value))}
                  className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                >
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={handleCompare}
                  className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-500"
                >
                  Compare
                </button>
              </div>

              {compareResult ? (
                <div className="mt-5 grid gap-4 md:grid-cols-2">
                  <ComparePanel label={compareResult.a.role.name} result={compareResult.a} />
                  <ComparePanel label={compareResult.b.role.name} result={compareResult.b} />
                </div>
              ) : null}
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
      <div className="text-xs uppercase tracking-[0.2rem] text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-bold text-white">{value}</div>
    </div>
  )
}

function MetricCard({
  label,
  value,
  suffix,
  tone,
}: {
  label: string
  value: number | string
  suffix?: string
  tone: "violet" | "cyan" | "amber"
}) {
  const toneClasses = {
    violet: "border-violet-500/30 bg-violet-500/10 text-violet-100",
    cyan: "border-cyan-500/30 bg-cyan-500/10 text-cyan-100",
    amber: "border-amber-500/30 bg-amber-500/10 text-amber-100",
  }

  return (
    <div className={`rounded-xl border p-4 ${toneClasses[tone]}`}>
      <div className="text-xs uppercase tracking-[0.18rem] text-slate-300">{label}</div>
      <div className="mt-2 text-3xl font-bold text-white">
        {value}
        {suffix ? <span className="ml-1 text-sm text-slate-300">{suffix}</span> : null}
      </div>
    </div>
  )
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950/70 p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2rem] text-slate-400">{title}</h3>
      {children}
    </div>
  )
}

function ComparePanel({ label, result }: { label: string; result: AnalysisResult }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950/60 p-4">
      <h4 className="mb-3 text-lg font-semibold text-white">{label}</h4>
      <div className="space-y-2 text-sm text-slate-300">
        <div>AI impact: {result.profile.overall_impact}%</div>
        <div>Automation: {result.profile.automation_pct}%</div>
        <div>Augmentation: {result.profile.augmentation_pct}%</div>
        <div>Human-led: {result.profile.human_pct}%</div>
      </div>
    </div>
  )
}
