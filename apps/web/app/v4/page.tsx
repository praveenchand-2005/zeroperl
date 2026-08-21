"use client";

import { useMemo, useState } from "react";

const profiles = [
  { platform: "Professional", name: "Demo Borrower A", company: "Example Technologies", position: "Software Engineer", location: "Chennai", confidence: 91, status: "UNVERIFIED" },
  { platform: "Public business page", name: "Demo Borrower A", company: "Example Technologies", position: "Consultant", location: "Chennai", confidence: 84, status: "UNVERIFIED" },
];

const employment = [
  { company: "Example Technologies", title: "Software Engineer", status: "CURRENT_CANDIDATE", confidence: 91 },
  { company: "Example Systems", title: "Developer", status: "HISTORICAL", confidence: 82 },
];

const companies = [
  { name: "Example Technologies", industry: "Technology", location: "Chennai", website: "Public source", confidence: 89, status: "PUBLIC_EVIDENCE" },
  { name: "Example Systems", industry: "IT Services", location: "Bengaluru", website: "Public source", confidence: 77, status: "PUBLIC_EVIDENCE" },
];

export default function V4Page() {
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState("Profiles");
  const filteredProfiles = useMemo(() => profiles.filter((item) => `${item.name} ${item.company} ${item.position}`.toLowerCase().includes(query.toLowerCase())), [query]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="border-b border-slate-800 pb-6">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-400">V4 Intelligence</p>
          <h1 className="mt-2 text-3xl font-semibold">Profile, Employment & Company Intelligence</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">Evidence-backed public/authorized professional and company intelligence connected to the existing case graph. Private profiles and private communications are excluded.</p>
        </header>

        <section className="grid gap-4 py-6 md:grid-cols-4">
          {[['Profile candidates', profiles.length.toString()], ['Employment records', employment.length.toString()], ['Company candidates', companies.length.toString()], ['Review required', '1']].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><div className="text-sm text-slate-500">{label}</div><div className="mt-2 text-2xl font-semibold">{value}</div></div>
          ))}
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-4">
            {['Profiles', 'Employment Timeline', 'Companies', 'Organization Graph'].map((item) => <button key={item} onClick={() => setTab(item)} className={`rounded-xl px-3 py-2 text-sm ${tab === item ? 'bg-cyan-400/10 text-cyan-300' : 'text-slate-500'}`}>{item}</button>)}
          </div>

          {tab === 'Profiles' && <div className="pt-5"><div className="flex justify-between gap-3"><div><h2 className="text-lg font-semibold">Public Profile Candidates</h2><p className="text-sm text-slate-500">Candidates remain unverified until a permitted verification process confirms them.</p></div><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter profiles" className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm" /></div><div className="mt-4 grid gap-3">{filteredProfiles.map((item) => <div key={`${item.platform}-${item.name}`} className="grid gap-4 rounded-xl border border-slate-800 bg-slate-950 p-4 md:grid-cols-[1fr_1fr_1fr_120px]"><div><div className="text-xs text-slate-500">Profile</div><div className="mt-1 font-medium">{item.name}</div><div className="text-xs text-slate-500">{item.platform}</div></div><div><div className="text-xs text-slate-500">Company</div><div className="mt-1">{item.company}</div><div className="text-xs text-slate-500">{item.location}</div></div><div><div className="text-xs text-slate-500">Position</div><div className="mt-1">{item.position}</div></div><div className="text-right"><div className="text-xs text-slate-500">Confidence</div><div className="mt-1 text-xl font-semibold">{item.confidence}%</div><div className="text-xs text-amber-300">{item.status}</div></div></div>)}</div></div>}

          {tab === 'Employment Timeline' && <div className="pt-5"><h2 className="text-lg font-semibold">Employment Timeline</h2><div className="mt-6 space-y-4">{employment.map((item) => <div key={`${item.company}-${item.title}`} className="flex items-center gap-4"><div className="h-3 w-3 rounded-full bg-cyan-400" /><div className="flex-1 rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="flex justify-between gap-4"><div><div className="font-medium">{item.company}</div><div className="text-sm text-slate-400">{item.title}</div></div><div className="text-right"><div className="font-semibold">{item.confidence}%</div><div className="text-xs text-slate-500">{item.status}</div></div></div></div></div>)}</div><p className="mt-5 text-sm text-slate-500">Current employment is shown as a candidate unless supported by an authorized verification source.</p></div>}

          {tab === 'Companies' && <div className="pt-5"><h2 className="text-lg font-semibold">Company Intelligence</h2><div className="mt-4 grid gap-3 md:grid-cols-2">{companies.map((item) => <div key={item.name} className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="flex justify-between"><div><div className="font-medium">{item.name}</div><div className="text-sm text-slate-400">{item.industry}</div></div><div className="text-right font-semibold">{item.confidence}%</div></div><div className="mt-4 grid grid-cols-2 gap-3 text-sm"><div><div className="text-xs text-slate-500">Location</div><div className="mt-1">{item.location}</div></div><div><div className="text-xs text-slate-500">Website</div><div className="mt-1">{item.website}</div></div></div><div className="mt-4 text-xs text-amber-300">{item.status}</div></div>)}</div></div>}

          {tab === 'Organization Graph' && <div className="pt-5"><h2 className="text-lg font-semibold">Evidence-backed Organization Graph</h2><div className="mt-6 grid gap-4 text-center md:grid-cols-5"><div className="rounded-xl border border-cyan-400/30 bg-cyan-400/5 p-4"><div className="text-xs text-slate-500">PERSON</div><div className="mt-2 font-medium">Demo Borrower A</div></div><div className="self-center text-slate-600">→</div><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">COMPANY</div><div className="mt-2 font-medium">Example Technologies</div></div><div className="self-center text-slate-600">→</div><div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">POSITION</div><div className="mt-2">Software Engineer</div></div></div><div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm"><div className="font-medium">Relationship rule</div><div className="mt-1 text-slate-500">A reporting relationship is never inferred merely from two people working at the same company. It requires explicit supporting evidence or an authorized source.</div></div></div>}
        </section>
      </div>
    </main>
  );
}
