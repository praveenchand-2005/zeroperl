'use client';

import { useMemo, useState } from 'react';

const cases = [
  { id: 'CASE-2026-00482', borrower: 'Ravi Kumar', lender: 'Example Bank', dpd: 142, balance: '₹4.82L', priority: 'High', confidence: 91, status: 'Investigation' },
  { id: 'CASE-2026-00471', borrower: 'Anita Sharma', lender: 'Example NBFC', dpd: 98, balance: '₹2.14L', priority: 'Medium', confidence: 78, status: 'Field Verify' },
  { id: 'CASE-2026-00455', borrower: 'S. Prakash', lender: 'Example Bank', dpd: 67, balance: '₹86K', priority: 'Low', confidence: 64, status: 'Review' },
];

const modules = [
  ['Cases', 'Recovery case management'],
  ['Investigations', 'AI + evidence workflows'],
  ['Scraper', 'Authorized source acquisition'],
  ['Evidence Graph', 'Entity + relationship graph'],
  ['Field Operations', 'Visits and verification'],
  ['V4 Intelligence', 'Public profile + employment + company'],
];

export default function Home() {
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => cases.filter((c) => `${c.id} ${c.borrower} ${c.lender}`.toLowerCase().includes(query.toLowerCase())), [query]);

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">RI</span><div><strong>Recovery Intelligence</strong><small>Enterprise SaaS · V1–V4</small></div></div>
        <nav>
          {['Dashboard','Cases','Investigations','Field Operations','Evidence','V4 Intelligence','Reports','Analytics','Compliance','Audit','Settings'].map((item, i) => (
            <button key={item} className={i === 0 ? 'nav active' : 'nav'}>{item}</button>
          ))}
        </nav>
        <div className="tenant"><small>Workspace</small><b>Recovery Agency A</b><span>Admin · Multi-tenant</span></div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div><small>Operations Console</small><h1>Recovery intelligence dashboard</h1></div>
          <div className="top-actions"><span className="status-dot"/> All systems ready <button className="avatar">PC</button></div>
        </header>

        <section className="hero-grid">
          <div className="hero-card">
            <div><span className="eyebrow">V1–V4 unified workflow</span><h2>Investigate. Correlate. Verify. Recover.</h2><p>Start from an authorized case, gather permitted evidence, resolve candidate identities and move verified findings into field recovery.</p></div>
            <button className="primary" onClick={() => alert('Investigation workflow scaffold is ready for backend integration.')}>Run investigation</button>
          </div>
          <div className="score-card"><span>Portfolio confidence</span><strong>84%</strong><small>Across active investigations</small><div className="meter"><i style={{width:'84%'}}/></div></div>
        </section>

        <section className="stats">
          {[
            ['Active Cases','128','+12 this week'],
            ['Investigations','43','18 running'],
            ['Field Visits','31','9 scheduled today'],
            ['Evidence Items','2,481','96 added today'],
          ].map(([label,value,meta]) => <article className="stat" key={label}><span>{label}</span><strong>{value}</strong><small>{meta}</small></article>)}
        </section>

        <section className="panel">
          <div className="panel-head"><div><h3>Priority cases</h3><p>Cases currently needing investigation or human review.</p></div><input placeholder="Search case / borrower / lender" value={query} onChange={(e) => setQuery(e.target.value)} /></div>
          <div className="table-wrap"><table><thead><tr><th>Case</th><th>Borrower</th><th>Lender</th><th>DPD</th><th>Balance</th><th>Confidence</th><th>Status</th></tr></thead><tbody>
            {filtered.map((c) => <tr key={c.id}><td><b>{c.id}</b><small className={`pill ${c.priority.toLowerCase()}`}>{c.priority}</small></td><td>{c.borrower}</td><td>{c.lender}</td><td>{c.dpd} days</td><td>{c.balance}</td><td><b>{c.confidence}%</b><div className="mini-meter"><i style={{width:`${c.confidence}%`}}/></div></td><td><span className="status-pill">{c.status}</span></td></tr>)}
          </tbody></table></div>
        </section>

        <section className="modules"><div className="panel-head"><div><h3>Platform modules</h3><p>V1–V4 layers are designed to share the same case, evidence and audit backbone.</p></div></div><div className="module-grid">{modules.map(([name,desc]) => <article key={name}><div className="module-icon">{name[0]}</div><div><b>{name}</b><p>{desc}</p></div><span>→</span></article>)}</div></section>
      </section>

      <style jsx>{`
        *{box-sizing:border-box} body{margin:0;background:#07111f;color:#e8eef8;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}.shell{min-height:100vh;display:grid;grid-template-columns:250px 1fr;background:radial-gradient(circle at 80% -10%,#17305b55,transparent 40%),#07111f}.sidebar{border-right:1px solid #1c2a40;padding:24px 16px;display:flex;flex-direction:column;gap:24px;background:#091423}.brand{display:flex;align-items:center;gap:10px}.brand strong{display:block;font-size:14px}.brand small{color:#77869d;font-size:11px}.brand-mark{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:linear-gradient(135deg,#5b8cff,#7d5cff);font-size:12px;font-weight:800}.sidebar nav{display:grid;gap:6px}.nav{border:0;background:transparent;color:#8e9bb0;text-align:left;padding:11px 12px;border-radius:10px;font-size:13px;cursor:pointer}.nav.active,.nav:hover{background:#132239;color:#fff}.tenant{margin-top:auto;padding:12px;border:1px solid #1e2d42;background:#0c1829;border-radius:12px;display:grid;gap:3px}.tenant small,.tenant span{color:#728197;font-size:11px}.content{padding:28px 30px 50px;max-width:1500px;width:100%;margin:0 auto}.topbar{display:flex;justify-content:space-between;align-items:end;margin-bottom:24px}.topbar small{color:#6f819b;text-transform:uppercase;letter-spacing:.12em;font-size:10px}.topbar h1{margin:5px 0 0;font-size:28px}.top-actions{display:flex;gap:10px;align-items:center;color:#8ea0b7;font-size:12px}.status-dot{width:8px;height:8px;border-radius:50%;background:#42d392;box-shadow:0 0 14px #42d39266}.avatar{border:1px solid #273950;background:#122138;color:#fff;border-radius:9px;width:34px;height:34px}.hero-grid{display:grid;grid-template-columns:1fr 270px;gap:16px}.hero-card,.score-card,.panel,.modules{background:#0c1829;border:1px solid #1d2c43;border-radius:16px}.hero-card{padding:26px;display:flex;justify-content:space-between;gap:30px;align-items:end;min-height:205px;background:linear-gradient(135deg,#122542,#0c1829)}.eyebrow{color:#7ea4ff;font-size:11px;text-transform:uppercase;letter-spacing:.12em}.hero-card h2{margin:8px 0;font-size:30px;max-width:620px}.hero-card p,.panel-head p{margin:0;color:#8190a6;line-height:1.6;font-size:13px}.primary{border:0;background:#6f7cff;color:white;border-radius:10px;padding:12px 18px;font-weight:700;white-space:nowrap;cursor:pointer}.score-card{padding:24px;display:grid;align-content:center;gap:8px}.score-card span,.stat span{color:#7b8aa1;font-size:12px}.score-card strong{font-size:48px}.score-card small,.stat small{color:#6f8198}.meter,.mini-meter{height:5px;border-radius:99px;background:#1b2a3e;overflow:hidden}.meter i,.mini-meter i{display:block;height:100%;background:linear-gradient(90deg,#5b8cff,#7b6dff);border-radius:inherit}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0}.stat{background:#0c1829;border:1px solid #1d2c43;border-radius:14px;padding:18px;display:grid;gap:7px}.stat strong{font-size:26px}.panel,.modules{padding:20px;margin-top:16px}.panel-head{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:16px}.panel-head h3{margin:0 0 4px;font-size:16px}.panel-head input{background:#091423;border:1px solid #26384f;color:#fff;border-radius:9px;padding:10px 12px;min-width:300px;outline:none}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:12px}th,td{text-align:left;padding:13px 10px;border-top:1px solid #1b2a3f;white-space:nowrap}th{color:#6f8198;font-size:10px;text-transform:uppercase;letter-spacing:.08em}td b{color:#eef4fc}.pill{display:inline-block;margin-left:7px;padding:3px 6px;border-radius:5px;font-size:9px}.pill.high{background:#48212a;color:#ff9da9}.pill.medium{background:#44371b;color:#f6cb70}.pill.low{background:#1c3d31;color:#83ddb6}.status-pill{border:1px solid #2a3c54;border-radius:999px;padding:5px 8px;color:#b7c4d8;background:#101e31}.mini-meter{width:65px;margin-top:5px}.module-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.module-grid article{display:flex;align-items:center;gap:12px;padding:14px;border:1px solid #1c2c43;background:#091423;border-radius:12px}.module-icon{width:30px;height:30px;border-radius:8px;display:grid;place-items:center;background:#162640;color:#8fb0ff;font-weight:800}.module-grid p{margin:3px 0 0;color:#728199;font-size:11px}.module-grid article>span{margin-left:auto;color:#66788e}@media(max-width:1000px){.shell{grid-template-columns:1fr}.sidebar{display:none}.content{padding:20px}.hero-grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.module-grid{grid-template-columns:1fr}.topbar{align-items:start;gap:15px}.top-actions{display:none}}@media(max-width:650px){.stats{grid-template-columns:1fr}.hero-card{flex-direction:column;align-items:start}.panel-head{flex-direction:column;align-items:stretch}.panel-head input{min-width:0;width:100%}}
      `}</style>
    </main>
  );
}
