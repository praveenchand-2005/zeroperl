"use client";

import { useState } from "react";

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

export default function HomePage() {
  const [query, setQuery] = useState("");
  const filtered = demoCases.filter((item) =>
    `${item.id} ${item.borrower} ${item.status}`.toLowerCase().includes(query.toLowerCase()),
  );

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
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search cases..."
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none ring-cyan-400/30 focus:ring"
              />
            </div>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase tracking-wide text-slate-500">
                  <tr className="border-b border-slate-800">
                    <th className="px-3 py-3">Case</th>
                    <th className="px-3 py-3">Borrower</th>
                    <th className="px-3 py-3">Priority</th>
                    <th className="px-3 py-3">Identity</th>
                    <th className="px-3 py-3">Address</th>
                    <th className="px-3 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((item) => (
                    <tr key={item.id} className="border-b border-slate-800/70">
                      <td className="px-3 py-3 font-medium">{item.id}</td>
                      <td className="px-3 py-3 text-slate-300">{item.borrower}</td>
                      <td className="px-3 py-3"><span className="rounded-full bg-amber-400/10 px-2 py-1 text-xs text-amber-300">{item.priority}</span></td>
                      <td className="px-3 py-3">{item.identity}%</td>
                      <td className="px-3 py-3">{item.address}%</td>
                      <td className="px-3 py-3 text-slate-400">{item.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <h2 className="text-lg font-semibold">Investigation Controls</h2>
            <div className="mt-4 space-y-3 text-sm">
              {[
                ["Source Registry", "Configure organization-approved sources and allowed fields"],
                ["Evidence", "Review provenance, confidence and verification state"],
                ["Field Operations", "Send human-reviewed address candidates for verification"],
                ["Audit", "Track sensitive access and investigation actions"],
              ].map(([title, body]) => (
                <div key={title} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                  <div className="font-medium">{title}</div>
                  <div className="mt-1 text-slate-500">{body}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
