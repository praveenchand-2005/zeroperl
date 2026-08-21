"use client";

import { useMemo, useState } from "react";

const modules = [
  ["V1", "Cases & Recovery", "Case management, field operations, communications and audit"],
  ["V2", "Data Acquisition", "Approved sources, scraping jobs and evidence provenance"],
  ["V3", "Public Intelligence", "Government, regulatory and public-record investigation"],
  ["V4", "Profile & Company", "Public professional, employment and company intelligence"],
];

const demoCases = [
  { id: "CASE-2026-001", borrower: "Demo Borrower A", priority: "HIGH", identity: 94, address: 88, status: "INVESTIGATION" },
  { id: "CASE-2026-002", borrower: "Demo Borrower B", priority: "MEDIUM", identity: 81, address: 73, status: "FIELD_VERIFICATION" },
  { id: "CASE-2026-003", borrower: "Demo Borrower C", priority: "LOW", identity: 96, address: 91, status: "RECOVERY" },
];

const demoEvidence = [
  { source: "Official public record", field: "Name + city", value: "Demo Borrower A / Chennai", confidence: 0.94, status: "SOURCE_REPORTED" },
  { source: "Public business record", field: "Address", value: "12 Example Road, Chennai", confidence: 0.88, status: "UNVERIFIED" },
  { source: "Public company page", field: "Organization", value: "Example Technologies", confidence: 0.81, status: "PUBLIC_EVIDENCE" },
];

const reviewItems = [
  { id: "REV-001", type: "ADDRESS_CONFLICT", reason: "Two recent sources report different candidate addresses.", priority: "HIGH" },
  { id: "REV-002", type: "IDENTITY_MATCH", reason: "Strong name/location match but no authorized identity verification.", priority: "MEDIUM" },
];

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState("Overview");
  const [selectedCase, setSelectedCase] = useState(demoCases[0]);
  const [reviewMessage, setReviewMessage] = useState("");

  const filtered = useMemo(
    () => demoCases.filter((item) => `${item.id} ${item.borrower} ${item.status}`.toLowerCase().includes(query.toLowerCase())),
    [query],
  );

  const tabs = ["Overview", "Investigation", "Evidence", "Graph", "Review Queue", "Sources", "Audit"];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="flex flex-col gap-5 border-b border-slate-800 pb-7 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-400">Enterprise Recovery Intelligence</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">Recovery Intelligence Platform</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-400">Case-scoped investigation, evidence acquisition and recovery operations for authorized organizations.</p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm">
            <div className="text-slate-500">Workspace</div>
            <div className="font-medium">Demo Organization</div>
          </div>
        </header>

        <section className="grid gap-4 py-6 md:grid-cols-4">
          {[
            ["Active Cases", "128"],
            ["Investigations", "37"],
            ["Field Visits", "19"],
            ["Evidence Items", "2,481"],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="text-sm text-slate-500">{label}</div>
              <div className="mt-2 text-2xl font-semibold">{value}</div>
            </div>
          ))}
        </section>

        <section className="grid gap-4 md:grid-cols-4">
          {modules.map(([version, title, description]) => (
            <div key={version} className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="inline-flex rounded-lg bg-cyan-400/10 px-2.5 py-1 text-xs font-semibold text-cyan-300">{version}</div>
              <h2 className="mt-4 text-lg font-semibold">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Priority Cases</h2>
                <p className="text-sm text-slate-500">Synthetic demo records only.</p>
              </div>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search cases..." className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none ring-cyan-400/30 focus:ring" />
            </div>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase tracking-wide text-slate-500"><tr className="border-b border-slate-800"><th className="px-3 py-3">Case</th><th className="px-3 py-3">Borrower</th><th className="px-3 py-3">Priority</th><th className="px-3 py-3">Identity</th><th className="px-3 py-3">Address</th><th className="px-3 py-3">Status</th></tr></thead>
                <tbody>
                  {filtered.map((item) => (
                    <tr key={item.id} onClick={() => setSelectedCase(item)} className={`cursor-pointer border-b border-slate-800/70 ${selectedCase.id === item.id ? "bg-cyan-400/5" : ""}`}>
                      <td className="px-3 py-3 font-medium">{item.id}</td><td className="px-3 py-3 text-slate-300">{item.borrower}</td><td className="px-3 py-3"><span className="rounded-full bg-amber-400/10 px-2 py-1 text-xs text-amber-300">{item.priority}</span></td><td className="px-3 py-3">{item.identity}%</td><td className="px-3 py-3">{item.address}%</td><td className="px-3 py-3 text-slate-400">{item.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <h2 className="text-lg font-semibold">Investigation Controls</h2>
            <div className="mt-4 space-y-3 text-sm">
              {["Source Registry", "Evidence", "Field Operations", "Audit"].map((title) => <div key={title} className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="font-medium">{title}</div><div className="mt-1 text-slate-500">Organization-scoped controls and provenance.</div></div>)}
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-4">
            {tabs.map((tab) => <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-xl px-3 py-2 text-sm ${activeTab === tab ? "bg-cyan-400/10 text-cyan-300" : "text-slate-500 hover:text-slate-300"}`}>{tab}</button>)}
          </div>

          <div className="pt-5">
            {activeTab === "Overview" && <div className="grid gap-4 md:grid-cols-4"><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">Selected Case</div><div className="mt-2 font-semibold">{selectedCase.id}</div></div><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">Identity Confidence</div><div className="mt-2 text-2xl font-semibold">{selectedCase.identity}%</div></div><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">Address Confidence</div><div className="mt-2 text-2xl font-semibold">{selectedCase.address}%</div></div><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">Status</div><div className="mt-2 font-semibold">{selectedCase.status}</div></div></div>}

            {activeTab === "Investigation" && <div className="grid gap-4 md:grid-cols-3"><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">Search Plan</div><div className="mt-3 space-y-2 text-sm"><div>✓ Identity seed normalization</div><div>✓ Approved source selection</div><div>→ Public record execution</div><div>→ Entity resolution</div><div>→ Human review</div></div></div><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">Execution</div><div className="mt-3 h-2 rounded-full bg-slate-800"><div className="h-2 w-2/3 rounded-full bg-cyan-400" /></div><div className="mt-2 text-sm text-slate-400">66% • 4/6 jobs complete</div></div><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">Next Action</div><div className="mt-2 font-medium">Review address conflict</div><div className="mt-1 text-sm text-slate-500">Human verification required before escalation.</div></div></div>}

            {activeTab === "Evidence" && <div className="space-y-3">{demoEvidence.map((item) => <div key={`${item.source}-${item.field}`} className="grid gap-2 rounded-xl border border-slate-800 bg-slate-950 p-4 md:grid-cols-[1fr_1fr_1fr_auto]"><div><div className="text-xs text-slate-500">Source</div><div className="mt-1 font-medium">{item.source}</div></div><div><div className="text-xs text-slate-500">Field</div><div className="mt-1">{item.field}</div></div><div><div className="text-xs text-slate-500">Value</div><div className="mt-1 text-slate-300">{item.value}</div></div><div className="text-right"><div className="text-xs text-slate-500">Confidence</div><div className="mt-1 font-semibold">{Math.round(item.confidence * 100)}%</div><div className="text-xs text-slate-500">{item.status}</div></div></div>)}</div>}

            {activeTab === "Graph" && <div className="rounded-xl border border-slate-800 bg-slate-950 p-5"><div className="grid gap-4 text-center md:grid-cols-5"><div className="rounded-xl border border-cyan-400/30 p-4"><div className="text-xs text-slate-500">PERSON</div><div className="mt-2 font-medium">{selectedCase.borrower}</div></div><div className="self-center text-slate-600">→</div><div className="rounded-xl border border-slate-800 p-4"><div className="text-xs text-slate-500">ADDRESS</div><div className="mt-2">Candidate A</div></div><div className="self-center text-slate-600">→</div><div className="rounded-xl border border-slate-800 p-4"><div className="text-xs text-slate-500">EVIDENCE</div><div className="mt-2">3 independent sources</div></div></div><p className="mt-5 text-sm text-slate-500">Graph edges retain provenance, confidence and verification status. Demo visualization only.</p></div>}

            {activeTab === "Review Queue" && <div className="space-y-3">{reviewItems.map((item) => <div key={item.id} className="flex flex-col gap-4 rounded-xl border border-slate-800 bg-slate-950 p-4 md:flex-row md:items-center md:justify-between"><div><div className="flex items-center gap-2"><span className="font-medium">{item.id}</span><span className="rounded-full bg-rose-400/10 px-2 py-1 text-xs text-rose-300">{item.priority}</span></div><div className="mt-1 text-sm text-slate-400">{item.type} • {item.reason}</div></div><button onClick={() => setReviewMessage(`Review ${item.id} selected for manager decision.`)} className="rounded-xl border border-slate-700 px-3 py-2 text-sm hover:bg-slate-800">Open Review</button></div>)}{reviewMessage && <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-4 text-sm text-cyan-200">{reviewMessage}</div>}</div>}

            {activeTab === "Sources" && <div className="grid gap-3 md:grid-cols-3">{[["Gov/Public Registry", "PUBLIC_RECORD", "Enabled"], ["Public Business Source", "BUSINESS", "Enabled"], ["Authorized Verification", "AUTHORIZED_API", "Configured by admin"]].map(([name, type, state]) => <div key={name} className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="font-medium">{name}</div><div className="mt-1 text-xs text-slate-500">{type}</div><div className="mt-3 text-xs text-cyan-300">{state}</div></div>)}</div>}

            {activeTab === "Audit" && <div className="space-y-3 text-sm">{["CASE_VIEW", "INVESTIGATION_QUEUED", "SOURCE_ACCESSED", "EVIDENCE_REVIEW", "REVIEW_DECISION"].map((event, index) => <div key={event} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950 p-4"><div><div className="font-medium">{event}</div><div className="text-xs text-slate-500">CASE-2026-001 • Demo organization</div></div><div className="text-xs text-slate-500">{index + 1} min ago</div></div>)}</div>}
          </div>
        </section>
      </div>
    </main>
  );
}
