import React, {useEffect, useState} from 'react';
import {api, ThemeToggle, SourceLink, Icon, ErrorNotice} from './ui';

type Check = {id:string;title:string;passed:boolean;observed:string};
type Run = {id:string;brand:string;brief:string;features:string[];stage:string;revision:number;tasks:any[];criteria:string[];design:string[];trace:any[];qa:null|{passed:boolean;checks:Check[];stdout:string;stderr:string;command:string;exit_code:number;executed_at:string};decision:null|{note:string;at:string;source_hash:string};fault:string;diff:string;files:{name:string;content:string;bytes:number}[];preview_html:string;workspace_path:string;source_hash:string};
type State = {run:Run;active_run_id:string;runs:{id:string;brand:string;stage:string;revision:number;updated_at:string}[];features:{id:string;title:string;description:string}[];provider:any};
type Tab = 'brief'|'source'|'checks'|'activity';
const stages = [{id:'brief',label:'Product brief',icon:'FileText',worker:'Owner'},{id:'planned',label:'Delivery plan',icon:'Layers',worker:'Planner'},{id:'designed',label:'Technical design',icon:'GitBranch',worker:'Architect'},{id:'built',label:'Source build',icon:'Code2',worker:'Builder'},{id:'reviewed',label:'Quality review',icon:'ShieldCheck',worker:'Reviewer'},{id:'accepted',label:'Acceptance',icon:'CheckCircle2',worker:'Owner'}];
const tabLabels:{id:Tab;label:string;icon:string}[]=[{id:'brief',label:'Brief',icon:'FileText'},{id:'source',label:'Source',icon:'Code2'},{id:'checks',label:'Checks',icon:'ShieldCheck'},{id:'activity',label:'Activity',icon:'Activity'}];
function time(value:string){return new Date(value).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'})}

export default function App(){
  const [state,setState]=useState<State|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState('');
  const [tab,setTab]=useState<Tab>((new URLSearchParams(location.search).get('tab') as Tab)||'brief');
  const [brand,setBrand]=useState('Northline'),[brief,setBrief]=useState(''),[features,setFeatures]=useState<string[]>([]);
  const [source,setSource]=useState('catalog.mjs'),[showDiff,setShowDiff]=useState(false),[previewWidth,setPreviewWidth]=useState('full'),[previewTheme,setPreviewTheme]=useState('light');
  const [fault,setFault]=useState('wrong_total'),[note,setNote]=useState('Reviewed the storefront and executable checks. Ready to keep this artifact.'),[newDraft,setNewDraft]=useState(false);
  useEffect(()=>{api.state().then((s:State)=>{setState(s);setBrand(s.run.brand);setBrief(s.run.brief);setFeatures(s.run.features)}).catch(e=>setError(e.message))},[]);
  const run=state?.run;
  const active=stages.findIndex(s=>s.id===run?.stage);
  const sync=(s:State,updateDraft=false)=>{setState(s);if(updateDraft){setBrand(s.run.brand);setBrief(s.run.brief);setFeatures(s.run.features);setNewDraft(false)}};
  async function action(name:string,payload:any={}){
    setError('');setBusy(name);
    try{const s=await api.action(name,{run_id:run?.id,...payload});sync(s,name==='select');if(name==='qa')setTab('checks');if(name==='repair'||name==='inject'){setTab('source');setShowDiff(true)}return s;}catch(e:any){setError(e.message)}finally{setBusy('')}
  }
  async function build(){
    setError('');setBusy('Preparing brief');
    try{
      let s:State=await api.action('create',{brand,brief,features});sync(s);setNewDraft(false);
      for(const [name,label] of [['plan','Planning scope'],['design','Designing source'],['build','Writing artifact']]){setBusy(label);s=await api.action(name,{run_id:s.active_run_id});sync(s)}
      setTab('source');setShowDiff(false);
    }catch(e:any){setError(e.message)}finally{setBusy('')}
  }
  async function exportArtifact(){setError('');setBusy('export');try{const result=await api.action('export',{run_id:run?.id});const bytes=Uint8Array.from(atob(result.base64),(c)=>c.charCodeAt(0));const href=URL.createObjectURL(new Blob([bytes],{type:'application/zip'}));const link=document.createElement('a');link.href=href;link.download=result.filename;link.click();setTimeout(()=>URL.revokeObjectURL(href),1500)}catch(e:any){setError(e.message)}finally{setBusy('')}}
  function newWorkflow(){setNewDraft(true);setTab('brief');setBrand('Northline');setBrief('Build a storefront for considered everyday objects. Let visitors browse the collection, inspect materials, search by name, and compare a shopping bag total. Keep internal supplier costs out of the public catalog.');setFeatures(state?.features.map(f=>f.id)||[])}
  const selectedFile=run?.files.find(f=>f.name===source)||run?.files[0];
  const iframeHtml=run?.preview_html.replace('data-theme="light"',`data-theme="${previewTheme}"`);
  const passed=run?.qa?.checks.filter(c=>c.passed).length||0;
  const canAccept=run?.stage==='reviewed'&&run.qa?.passed;
  return <div className="crew-app">
    <header className="app-header"><div className="identity"><div className="crew-logo"><Icon name="GitBranch" size={21}/></div><strong>AgentCrew</strong><span className="product-divider"/><span className="header-context">Development workspace</span></div><div className="header-actions"><span className="worker-mode"><span/>Offline workers</span><SourceLink/><ThemeToggle/></div></header>
    <div className="workspace-layout">
      <aside className="run-rail" aria-label="Workflow navigation">
        <div className="rail-heading"><h2>Workflows</h2><button className="icon-button" onClick={newWorkflow} aria-label="New workflow" title="New workflow"><Icon name="Plus" size={17}/></button></div>
        <div className="active-project"><div className="project-symbol"><Icon name="Package" size={21}/></div><div><strong>{run?.brand||'Loading workspace'}</strong><span>{run?.id||'Preparing your files'}</span></div></div>
        <nav className="step-rail" aria-label="Delivery stages">{stages.map((stage,index)=>{
          const done=index<active||(index===active&&stage.id==='accepted');const current=index===active;
          return <button key={stage.id} className={`step ${done?'done':''} ${current?'current':''}`} onClick={()=>setTab(index>=4?'checks':index===3?'source':'brief')} aria-current={current?'step':undefined}><span className="step-dot"><Icon name={done?'Check':stage.icon} size={15}/></span><span><strong>{stage.label}</strong><small>{stage.worker}{done?' / complete':current?' / current':''}</small></span>{current&&<span className="current-mark"/>}</button>
        })}</nav>
        <div className="rail-history"><div className="history-title"><span>Recent runs</span><span>{state?.runs.length||0}</span></div>{state?.runs.map(r=><button className={`history-run ${r.id===run?.id?'selected':''}`} key={r.id} onClick={()=>action('select',{run_id:r.id})} disabled={!!busy}><Icon name="GitBranch" size={15}/><span><strong>{r.brand}</strong><small>r{String(r.revision).padStart(2,'0')} / {r.stage}</small></span><Icon name="ChevronRight" size={13}/></button>)}</div>
        <div className="rail-bottom"><Icon name="Database" size={15}/><span>Persisted locally<br/><strong>Source + SQLite history</strong></span></div>
      </aside>
      <section className="work-panel" aria-label="Workflow editor">
        <div className="editor-title"><div><h1>{newDraft?'New storefront':run?.brand||'Opening workspace'}</h1><p>{newDraft?'Define the next delivery':`Storefront / revision ${String(run?.revision||1).padStart(2,'0')}`}</p></div><span className={`stage-tag ${run?.stage==='accepted'?'success':''}`}><span/>{newDraft?'draft':run?.stage||'loading'}</span></div>
        <div className="editor-tabs" role="tablist" aria-label="Workspace views">{tabLabels.map(t=><button key={t.id} role="tab" aria-selected={tab===t.id} className={tab===t.id?'selected':''} onClick={()=>setTab(t.id)}><Icon name={t.icon} size={15}/>{t.label}{t.id==='checks'&&run?.qa&&<span className={run.qa.passed?'check-badge passed':'check-badge failed'}>{passed}/{run.qa.checks.length}</span>}</button>)}</div>
        <div className="editor-content">
          <ErrorNotice error={error}/>
          {busy&&<div className="working" role="status"><span className="working-dot"/>{busy==='qa'?'Executing Node.js checks':busy==='export'?'Packaging accepted source':busy}…</div>}
          {!state&&!error&&<div className="loading-workspace">Loading saved workflows…</div>}
          {tab==='brief'&&state&&<div className="brief-view">
            <div className="view-heading"><h2>Product brief</h2><span>Editable input</span></div>
            <label className="field">Store name<input value={brand} onChange={e=>setBrand(e.target.value)} maxLength={50} aria-label="Store name"/></label>
            <label className="field brief-field">What should we build?<textarea value={brief} onChange={e=>setBrief(e.target.value)} rows={6} maxLength={4000} aria-label="Product brief"/><span>{brief.length} / 4000 characters</span></label>
            <div className="scope-heading"><h3>Feature scope</h3><span>{features.length} selected</span></div>
            <div className="feature-list">{state.features.map(f=><label className={`feature-option ${features.includes(f.id)?'checked':''}`} key={f.id}><input type="checkbox" checked={features.includes(f.id)} onChange={()=>setFeatures(prev=>prev.includes(f.id)?prev.filter(id=>id!==f.id):[...prev,f.id])}/><span><strong>{f.title}</strong><small>{f.description}</small></span></label>)}</div>
            <button className="primary build-button" disabled={!!busy||features.length===0||brief.trim().length<20||brand.trim().length<2} onClick={build}><Icon name="Play" size={16}/>{run?.stage==='brief'?'Build workflow':'Build new workflow'}<Icon name="ArrowRight" size={16}/></button>
            <p className="build-explainer">Planner → Architect → Builder. The selected scope becomes source files and a working preview.</p>
            <details className="working-detail"><summary>Acceptance criteria <span>{run?.criteria.length||0}</span></summary><ul>{run?.criteria.map(c=><li key={c}>{c}</li>)}</ul></details>
            <details className="working-detail"><summary>Technical design <span>{run?.design.length||0}</span></summary><ul>{run?.design.map(c=><li key={c}>{c}</li>)}</ul></details>
          </div>}
          {tab==='source'&&run&&<div className="source-view">
            <div className="source-controls"><label>File<select aria-label="Source file" value={selectedFile?.name||''} onChange={e=>{setSource(e.target.value);setShowDiff(false)}}>{run.files.map(f=><option key={f.name}>{f.name}</option>)}</select></label><button className={showDiff?'selected':''} onClick={()=>setShowDiff(!showDiff)} disabled={!run.diff} aria-pressed={showDiff}><Icon name="GitBranch" size={14}/>Diff</button></div>
            <div className="source-meta"><span>{showDiff?`Revision ${run.revision-1} → ${run.revision}`:selectedFile?.name}</span><span>{showDiff?'unified diff':`${selectedFile?.bytes||0} bytes`}</span></div>
            <div className={`code-scroll ${showDiff?'diff-view':''}`}><pre>{(showDiff?run.diff:selectedFile?.content||'Build a workflow to write source files.').split('\n').map((line,index)=><span className={`code-line ${showDiff&&line.startsWith('+')?'added':showDiff&&line.startsWith('-')?'removed':''}`} key={index}><span className="line-number">{index+1}</span><code>{line||' '}</code></span>)}</pre></div>
            <div className="fault-workbench"><div><Icon name="Activity" size={16}/><h3>Exercise the review gate</h3></div><p>Introduce a real source defect, observe failing checks, then repair it.</p><div className="fault-actions"><select value={fault} onChange={e=>setFault(e.target.value)} aria-label="Defect type"><option value="wrong_total" disabled={!run.features.includes('cart_total')}>Wrong bag total (+10%)</option><option value="leak_cost">Public supplier-cost leak</option></select><button onClick={()=>action('inject',{fault})} disabled={!!busy||active<3}><Icon name="Plus" size={14}/>Inject defect</button></div>{run.fault!=='none'&&<div className="repair-row"><span className="tag warning">{run.fault==='wrong_total'?'Arithmetic defect':'Supplier-cost leak'} present</span><button onClick={()=>action('repair')} disabled={!!busy}><Icon name="RefreshCw" size={14}/>Repair source</button></div>}</div>
            <details className="working-detail"><summary>Workspace path and source fingerprint</summary><code className="path-text">{run.workspace_path}</code><code className="path-text">SHA-256 {run.source_hash}</code></details>
          </div>}
          {tab==='checks'&&run&&<div className="checks-view">
            <div className="view-heading"><h2>Executable review</h2><span>Node.js</span></div>
            {run.qa?<><div className={`qa-verdict ${run.qa.passed?'passed':'failed'}`}><Icon name={run.qa.passed?'CheckCircle2':'AlertCircle'} size={23}/><div><strong>{run.qa.passed?'All checks passed':'Acceptance blocked'}</strong><span>{passed} of {run.qa.checks.length} checks / exit {run.qa.exit_code}</span></div></div><div className="checks-list">{run.qa.checks.map(check=><div className={`check-row ${check.passed?'passed':'failed'}`} key={check.id}><Icon name={check.passed?'Check':'X'} size={16}/><div><strong>{check.title}</strong><p>{check.observed}</p></div></div>)}</div><details className="command-output" open><summary><Icon name="Code2" size={14}/>Command output<span>{time(run.qa.executed_at)}</span></summary><pre><span className="command-line">$ {run.qa.command}</span>{'\n'}{run.qa.stdout}{run.qa.stderr&&'\n'+run.qa.stderr}</pre></details></>:<div className="empty-checks"><Icon name="ShieldCheck" size={32}/><h3>Source is ready for review</h3><p>Execute the same lookup, search, filtering and total logic used by the storefront. A failure blocks acceptance.</p><code>node qa.mjs</code><button className="primary" onClick={()=>action('qa')} disabled={!!busy||active<3}><Icon name="Play" size={15}/>Run checks</button></div>}
            {run.qa?.passed&&!run.decision&&<div className="acceptance-form"><h3>Keep this revision</h3><label>Review note<textarea value={note} onChange={e=>setNote(e.target.value)} rows={3} aria-label="Acceptance note"/></label><button className="primary" disabled={!!busy||!canAccept||note.trim().length<5} onClick={()=>action('accept',{note})}><Icon name="Check" size={16}/>Accept artifact</button></div>}
            {run.decision&&<div className="accepted-result"><Icon name="Package" size={20}/><h3>Revision {run.revision} accepted</h3><p>{run.decision.note}</p><button className="primary" onClick={exportArtifact} disabled={!!busy}><Icon name="Download" size={16}/>Download artifact ZIP</button><span>HTML, CSS, modules, fixtures, QA + acceptance record</span></div>}
          </div>}
          {tab==='activity'&&run&&<div className="activity-view"><div className="view-heading"><h2>Run activity</h2><span>{run.trace.length} events</span></div><div className="activity-list">{[...run.trace].reverse().map((event,i)=><div className="activity-event" key={i}><span className="activity-dot"/><div><div className="activity-event-heading"><strong>{event.title}</strong><time>{time(event.at)}</time></div><p>{event.detail}</p><span>{event.worker} / revision {event.revision}</span></div></div>)}</div><div className="worker-explanation"><Icon name="Layers" size={19}/><p>Workers are deterministic local programs. The builder writes fixed source templates; the reviewer starts real Node.js processes. No hosted model is configured.</p></div></div>}
        </div>
        <footer className="editor-footer"><span><span className={`status-dot ${run?.fault!=='none'?'warning':''}`}/>{busy?'Working':run?.decision?'Accepted source':run?.qa?.passed?'Ready for acceptance':run?.qa?'Repair needed':'Source written'}</span>{run&&active>=3&&<button className="primary" onClick={()=>action('qa')} disabled={!!busy}><Icon name="Play" size={14}/>{run.qa?'Rerun checks':'Run checks'}</button>}</footer>
      </section>
      <section className="preview-panel" aria-label="Live artifact preview">
        <div className="preview-heading"><div><Icon name="Eye" size={17}/><h2>Live artifact</h2></div><span className="live-state"><span/>Local preview</span></div>
        <div className="browser-toolbar"><div className="browser-location"><Icon name="ShieldCheck" size={13}/><span>{(run?.brand||'storefront').toLowerCase().replace(/\s/g,'-')}.local / index.html</span></div><div className="preview-actions"><button className={previewWidth==='full'?'selected':''} aria-label="Full preview width" onClick={()=>setPreviewWidth('full')}><Icon name="Layers" size={14}/></button><button className={previewWidth==='mobile'?'selected':''} aria-label="Narrow preview width" onClick={()=>setPreviewWidth('mobile')}><Icon name="PanelLeft" size={14}/></button><button onClick={()=>setPreviewTheme(previewTheme==='light'?'dark':'light')} aria-label="Switch artifact theme"><Icon name={previewTheme==='light'?'Moon':'Sun'} size={14}/></button></div></div>
        <div className={`artifact-stage ${previewWidth==='mobile'?'narrow':''}`}>
          {run?.preview_html?<iframe key={run.id+'-'+run.revision+'-'+previewTheme} title="Generated storefront" srcDoc={iframeHtml} sandbox="allow-scripts"/>:<div className="preview-empty"><Icon name="Code2" size={35}/><h2>Your artifact appears here</h2><p>Build the brief to write source files and open the live storefront.</p></div>}
        </div>
        <footer className="preview-footer"><span><Icon name="FileText" size={13}/>{run?.files.length||0} source files</span><span>r{String(run?.revision||1).padStart(2,'0')}{run?.decision?' / accepted':' / working artifact'}</span>{run?.decision&&<button onClick={exportArtifact} disabled={!!busy} aria-label="Download accepted storefront"><Icon name="Download" size={15}/></button>}</footer>
      </section>
    </div>
  </div>
}
