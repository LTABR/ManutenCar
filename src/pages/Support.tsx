import { useEffect, useMemo, useState, type FormEvent } from "react";
import { apiRequest } from "../api/client";

type TicketCategory = "Account/Login" | "Vehicle & Maintenance Calculations" | "System Bug" | "General Question";
type TicketStatus = "Open" | "In Progress" | "Resolved";
type Ticket = {
  id: string;
  category: TicketCategory;
  subject: string;
  description: string;
  status: TicketStatus;
  created_at: string;
};

const templates: Record<TicketCategory, string> = {
  "Account/Login": "I need help with my ManutenCar account. Details:",
  "Vehicle & Maintenance Calculations": "I have a question about a vehicle or maintenance calculation. Vehicle:",
  "System Bug": "I found a system issue. Steps to reproduce:",
  "General Question": "I would like help with:",
};

export function Support() {
  const [category, setCategory] = useState<TicketCategory>("General Question");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState(templates["General Question"]);
  const [statusFilter, setStatusFilter] = useState<TicketStatus | "">("");
  const [categoryFilter, setCategoryFilter] = useState<TicketCategory | "">("");
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [feedback, setFeedback] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function loadTickets() {
    const params = new URLSearchParams();
    if (categoryFilter) params.set("category", categoryFilter);
    if (statusFilter) params.set("status", statusFilter);
    const suffix = params.size ? `?${params.toString()}` : "";
    setTickets(await apiRequest<Ticket[]>(`/support/tickets${suffix}`));
  }

  useEffect(() => { void loadTickets(); }, [categoryFilter, statusFilter]);

  const visibleTickets = useMemo(() => tickets, [tickets]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setFeedback("");
    try {
      await apiRequest("/support/tickets", {
        method: "POST",
        body: JSON.stringify({ category, subject, description }),
      });
      setSubject("");
      setDescription(templates[category]);
      setFeedback("Ticket submitted successfully. Expected response SLA: up to 48 hours.");
      await loadTickets();
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "Unable to submit ticket.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="support-center" aria-labelledby="support-title">
      <div className="support-heading">
        <img src="/logo_ManutenCar.jpeg" alt="ManutenCar" className="support-logo" />
        <div><span className="support-kicker">CUSTOMER SUPPORT</span><h1 id="support-title">How can we help?</h1></div>
      </div>
      <div className="support-layout">
        <aside className="support-info">
          <h2>Contact & FAQ</h2>
          <p><strong>Email:</strong> suporte.manutencar@gmail.com</p>
          <p><strong>Response SLA:</strong> Up to 48 hours</p>
          <a href="#how-it-works">Maintenance and app guidelines</a>
          <a href="#planner">Vehicle and maintenance FAQ</a>
        </aside>
        <form className="support-form" onSubmit={submit}>
          <label>Issue category
            <select value={category} onChange={(event) => {
              const next = event.target.value as TicketCategory;
              setCategory(next);
              setDescription(templates[next]);
            }}>
              {Object.keys(templates).map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label>Subject<input value={subject} onChange={(event) => setSubject(event.target.value)} minLength={3} maxLength={160} required /></label>
          <label>Message<textarea value={description} onChange={(event) => setDescription(event.target.value)} minLength={10} maxLength={4000} required /></label>
          {feedback && <p className="support-feedback" role="status">{feedback}</p>}
          <button type="submit" disabled={submitting}>{submitting ? "Submitting..." : "Submit support ticket"}</button>
        </form>
      </div>
      <div className="ticket-history">
        <div className="ticket-filters">
          <h2>My tickets</h2>
          <select aria-label="Filter tickets by category" value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value as TicketCategory | "")}><option value="">All categories</option>{Object.keys(templates).map((item) => <option key={item} value={item}>{item}</option>)}</select>
          <select aria-label="Filter tickets by status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as TicketStatus | "")}><option value="">All statuses</option><option>Open</option><option>In Progress</option><option>Resolved</option></select>
        </div>
        {visibleTickets.length === 0 ? <p>No support tickets found.</p> : <div className="ticket-list">{visibleTickets.map((ticket) => (
          <article className="ticket-card" key={ticket.id}><div><strong>{ticket.subject}</strong><span>{ticket.category}</span></div><p>{ticket.description}</p><footer><b className={`ticket-status status-${ticket.status.toLowerCase().replace(" ", "-")}`}>{ticket.status}</b><time>{new Date(ticket.created_at).toLocaleString()}</time></footer></article>
        ))}</div>}
      </div>
    </section>
  );
}
