import { useEffect, useRef, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
type Viewer = 'agent' | 'customer';
type Ticket = { id: string; ticket_number: string; customer_email: string; order_id?: string; category: string; subject: string; description: string; priority: string; status: string; assigned_agent_id?: string; created_at: string; updated_at: string };
type Message = { id: string; sender_name: string; message: string; message_type: string; created_at: string };
type Event = { id: string; actor_name: string; event_type: string; old_value?: string; new_value?: string; created_at: string };
type Detail = Ticket & { messages: Message[]; events: Event[] };
type Agent = { id: string; name: string; email: string; role: string };
type Filters = { search: string; status: string; priority: string; category: string; assigned_agent_id: string };

const statuses = ['OPEN', 'IN_PROGRESS', 'WAITING_FOR_CUSTOMER', 'WAITING_FOR_PROVIDER', 'RESOLVED', 'CLOSED'];
const priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT'];
const categories = ['INSTALLATION', 'ACTIVATION', 'CONNECTIVITY', 'ORDER', 'TOPUP', 'REFUND', 'OTHER'];
const title = (value: string) => value.replaceAll('_', ' ');
const formatDate = (value: string) => new Date(value).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
const wsUrl = (path: string) => `${API.replace(/^http/, 'ws')}${path}`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function App() {
  const [mode, setMode] = useState<Viewer>('agent');
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selected, setSelected] = useState<Detail | null>(null);
  const [view, setView] = useState<'list' | 'create'>('list');
  const [filters, setFilters] = useState<Filters>({ search: '', status: '', priority: '', category: '', assigned_agent_id: '' });
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const load = () => {
    setLoading(true);
    const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value) as [string, string][]).toString();
    Promise.all([request<{ items: Ticket[] }>(`/tickets?${query}`), request<Agent[]>('/agents')])
      .then(([ticketResponse, agentResponse]) => { setTickets(ticketResponse.items); setAgents(agentResponse); setNotice(null); })
      .catch(() => setNotice({ type: 'error', text: 'Could not load tickets.' }))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filters.status, filters.priority, filters.category, filters.assigned_agent_id]);

  const openTicket = (id: string) => {
    request<Detail>(`/tickets/${id}?viewer=${mode}`).then(setSelected).catch(() => setNotice({ type: 'error', text: 'Could not load ticket.' }));
  };
  const changeMode = (nextMode: Viewer) => { setMode(nextMode); setSelected(null); setView('list'); };
  const showSuccess = (text: string) => { setNotice({ type: 'success', text }); window.setTimeout(() => setNotice(null), 3200); };

  return <div className="app">
    <header className="topbar">
      <div className="brand"><span className="mark">B</span><span>Badi Support</span></div>
      <nav className="primary-nav" aria-label="Primary navigation">
        <button className={view === 'list' ? 'active' : ''} onClick={() => { setView('list'); setSelected(null); }}>Tickets</button>
        <button className={view === 'create' ? 'active' : ''} onClick={() => { setView('create'); setSelected(null); }}>New ticket</button>
      </nav>
      <div className="mode-switch" role="group" aria-label="Demo view">
        <button className={mode === 'agent' ? 'selected' : ''} onClick={() => changeMode('agent')}>Agent</button>
        <button className={mode === 'customer' ? 'selected' : ''} onClick={() => changeMode('customer')}>Customer</button>
      </div>
    </header>
    <main>
      {notice && <div className={`notice ${notice.type}`} role="status">{notice.text}<button aria-label="Dismiss notification" onClick={() => setNotice(null)}>×</button></div>}
      {selected ? <TicketDetail ticket={selected} agents={agents} mode={mode} onBack={() => { setSelected(null); load(); }} onRefresh={() => openTicket(selected.id)} onNotify={showSuccess} onError={(text) => setNotice({ type: 'error', text })} /> : view === 'create' ? <CreateTicket mode={mode} onBack={() => setView('list')} onCreated={(id) => { setView('list'); showSuccess('Ticket created.'); openTicket(id); load(); }} onError={(text) => setNotice({ type: 'error', text })} /> : <TicketList mode={mode} tickets={tickets} agents={agents} filters={filters} setFilters={setFilters} loading={loading} onSearch={load} onOpen={openTicket} />}
    </main>
  </div>;
}

function TicketList({ mode, tickets, agents, filters, setFilters, loading, onSearch, onOpen }: { mode: Viewer; tickets: Ticket[]; agents: Agent[]; filters: Filters; setFilters: (filters: Filters) => void; loading: boolean; onSearch: () => void; onOpen: (id: string) => void }) {
  return <section>
    <div className="page-head"><div><p className="eyebrow">{mode === 'agent' ? 'Support workspace' : 'Your support cases'}</p><h1>Tickets</h1></div><span className="count">{tickets.length} shown</span></div>
    <div className="filters" aria-label="Ticket filters">
      <label className="search-field"><span className="sr-only">Search tickets</span><input aria-label="Search tickets" placeholder="Search tickets" value={filters.search} onChange={event => setFilters({ ...filters, search: event.target.value })} onKeyDown={event => event.key === 'Enter' && onSearch()} /></label>
      <Select ariaLabel="Filter by status" value={filters.status} onChange={value => setFilters({ ...filters, status: value })} options={statuses} placeholder="Status" />
      <Select ariaLabel="Filter by priority" value={filters.priority} onChange={value => setFilters({ ...filters, priority: value })} options={priorities} placeholder="Priority" />
      <Select ariaLabel="Filter by category" value={filters.category} onChange={value => setFilters({ ...filters, category: value })} options={categories} placeholder="Category" />
      {mode === 'agent' && <label className="select-field"><span className="sr-only">Filter by agent</span><select aria-label="Filter by agent" value={filters.assigned_agent_id} onChange={event => setFilters({ ...filters, assigned_agent_id: event.target.value })}><option value="">All agents</option>{agents.map(agent => <option key={agent.id} value={agent.id}>{agent.name}</option>)}</select></label>}
    </div>
    {loading ? <div className="state"><span className="spinner" />Loading tickets…</div> : tickets.length === 0 ? <div className="state"><strong>No tickets found</strong><span>Try changing the filters.</span></div> : <div className="ticket-table"><div className="table-head"><span>Ticket</span><span>Customer</span><span>Category</span><span>Priority</span><span>Status</span><span>Updated</span></div>{tickets.map(ticket => <button className="ticket-row" key={ticket.id} onClick={() => onOpen(ticket.id)}><span><strong>{ticket.ticket_number}</strong><b>{ticket.subject}</b></span><span>{ticket.customer_email}</span><span>{title(ticket.category)}</span><span><Badge value={ticket.priority} /></span><span><Badge value={ticket.status} /></span><span className="muted">{formatDate(ticket.updated_at)}</span></button>)}</div>}
  </section>;
}

function TicketDetail({ ticket, agents, mode, onBack, onRefresh, onNotify, onError }: { ticket: Detail; agents: Agent[]; mode: Viewer; onBack: () => void; onRefresh: () => void; onNotify: (text: string) => void; onError: (text: string) => void }) {
  const [text, setText] = useState('');
  const [internal, setInternal] = useState(false);
  const [saving, setSaving] = useState(false);
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connection = new WebSocket(wsUrl(`/ws/tickets/${ticket.id}?viewer=${mode}`));
    socket.current = connection;
    connection.onmessage = event => { const payload = JSON.parse(event.data); if (payload.event === 'new_message') onRefresh(); if (payload.event === 'error') onError(payload.message); };
    connection.onerror = () => onError('Real-time connection unavailable.');
    return () => { connection.close(); socket.current = null; };
  }, [ticket.id, mode]);

  const update = (body: Record<string, string | null>) => {
    setSaving(true);
    request(`/tickets/${ticket.id}`, { method: 'PATCH', body: JSON.stringify(body) }).then(() => { onRefresh(); onNotify('Ticket updated.'); }).catch(() => onError('Could not update ticket.')).finally(() => setSaving(false));
  };
  const send = () => {
    if (!text.trim()) return;
    setSaving(true);
    const payload = { message: text.trim(), type: mode === 'customer' ? 'CUSTOMER_REPLY' : internal ? 'INTERNAL_NOTE' : 'AGENT_REPLY', sender_name: mode === 'customer' ? ticket.customer_email : 'Support agent' };
    const connection = socket.current;
    const finish = () => { setText(''); setSaving(false); onNotify('Message sent.'); };
    if (connection?.readyState === WebSocket.OPEN) { connection.send(JSON.stringify(payload)); finish(); } else { request(`/tickets/${ticket.id}/messages?viewer=${mode}`, { method: 'POST', body: JSON.stringify(payload) }).then(finish).catch(() => { setSaving(false); onError('Could not send message.'); }); }
  };

  return <section>
    <button className="back" onClick={onBack}>← Tickets</button>
    <div className="detail-head"><div><p className="eyebrow">{ticket.ticket_number}</p><h1>{ticket.subject}</h1><p className="muted">{ticket.customer_email}{ticket.order_id && ` · ${ticket.order_id}`}</p></div>{mode === 'agent' && <div className="controls"><Select ariaLabel="Ticket status" value={ticket.status} onChange={value => update({ status: value })} options={statuses} disabled={saving} /><Select ariaLabel="Ticket priority" value={ticket.priority} onChange={value => update({ priority: value })} options={priorities} disabled={saving} /><label className="select-field"><span className="sr-only">Assigned agent</span><select aria-label="Assigned agent" value={ticket.assigned_agent_id ?? ''} onChange={event => update({ assigned_agent_id: event.target.value || null })} disabled={saving}><option value="">Unassigned</option>{agents.map(agent => <option key={agent.id} value={agent.id}>{agent.name}</option>)}</select></label></div>}</div>
    <div className="detail-grid"><div><div className="conversation"><div className="section-title"><h2>Conversation</h2><Badge value={ticket.status} /></div><p className="description">{ticket.description}</p>{ticket.messages.length === 0 ? <div className="empty-inline">No messages yet.</div> : ticket.messages.map(message => <div className={`message ${message.message_type === 'INTERNAL_NOTE' ? 'note' : ''}`} key={message.id}><div><strong>{message.sender_name}</strong>{message.message_type === 'INTERNAL_NOTE' && <span className="note-label">Internal note</span>}<span className="muted">{formatDate(message.created_at)}</span></div><p>{message.message}</p></div>)}</div><div className="composer"><label className="composer-label" htmlFor="message">{internal ? 'Internal note' : mode === 'customer' ? 'Reply to support' : 'Customer-visible reply'}</label><textarea id="message" aria-label="Message" placeholder={internal ? 'Add an internal note' : mode === 'customer' ? 'Write a reply to support' : 'Write a customer reply'} value={text} onChange={event => setText(event.target.value)} /><div className="composer-foot">{mode === 'agent' ? <label className="check-label"><input type="checkbox" checked={internal} onChange={event => setInternal(event.target.checked)} /> Internal note</label> : <span className="muted">Your reply is visible to support.</span>}<button className="primary" disabled={saving || !text.trim()} onClick={send}>{saving ? 'Sending…' : 'Send'}</button></div></div></div>{mode === 'agent' && <aside><div className="section-title"><h2>Activity</h2><span className="count">{ticket.events.length}</span></div>{ticket.events.length === 0 ? <p className="muted">No activity yet.</p> : ticket.events.map(event => <div className="event" key={event.id}><strong>{title(event.event_type)}</strong><span>{event.old_value ?? '—'} → {event.new_value ?? '—'}</span><small>{event.actor_name} · {formatDate(event.created_at)}</small></div>)}</aside>}</div>
  </section>;
}

function CreateTicket({ mode, onBack, onCreated, onError }: { mode: Viewer; onBack: () => void; onCreated: (id: string) => void; onError: (text: string) => void }) {
  const [form, setForm] = useState({ customer_email: '', order_id: '', category: 'CONNECTIVITY', subject: '', description: '', priority: 'MEDIUM' });
  const [saving, setSaving] = useState(false);
  const submit = (event: FormEvent) => { event.preventDefault(); setSaving(true); request<Ticket>('/tickets', { method: 'POST', body: JSON.stringify(form) }).then(ticket => onCreated(ticket.id)).catch(() => onError('Could not create ticket.')).finally(() => setSaving(false)); };
  return <section className="form-page"><button className="back" onClick={onBack}>← Tickets</button><p className="eyebrow">New ticket</p><h1>Create support ticket</h1><p className="form-intro">{mode === 'customer' ? 'Tell us what happened and we will follow up here.' : 'Create a case for a customer.'}</p><form onSubmit={submit}><label>Customer email<input required type="email" value={form.customer_email} onChange={event => setForm({ ...form, customer_email: event.target.value })} /></label><label>Order ID <span className="optional">Optional</span><input value={form.order_id} onChange={event => setForm({ ...form, order_id: event.target.value })} /></label><div className="form-row"><label>Category<Select ariaLabel="Ticket category" value={form.category} onChange={value => setForm({ ...form, category: value })} options={categories} /></label><label>Priority<Select ariaLabel="Ticket priority" value={form.priority} onChange={value => setForm({ ...form, priority: value })} options={priorities} /></label></div><label>Subject<input required value={form.subject} onChange={event => setForm({ ...form, subject: event.target.value })} /></label><label>Description<textarea required value={form.description} onChange={event => setForm({ ...form, description: event.target.value })} /></label><button className="primary full" disabled={saving}>{saving ? 'Creating…' : 'Create ticket'}</button></form></section>;
}

function Select({ ariaLabel, value, onChange, options, placeholder, disabled = false }: { ariaLabel: string; value: string; onChange: (value: string) => void; options: string[]; placeholder?: string; disabled?: boolean }) {
  return <label className="select-field"><span className="sr-only">{ariaLabel}</span><select aria-label={ariaLabel} value={value} onChange={event => onChange(event.target.value)} disabled={disabled}>{placeholder && <option value="">{placeholder}</option>}{options.map(option => <option key={option} value={option}>{title(option)}</option>)}</select></label>;
}

function Badge({ value }: { value: string }) { return <span className={`badge ${value.toLowerCase()}`}>{title(value)}</span>; }
function AppShell({ children }: { children: ReactNode }) { return children; }

createRoot(document.getElementById('root')!).render(<AppShell><App /></AppShell>);
