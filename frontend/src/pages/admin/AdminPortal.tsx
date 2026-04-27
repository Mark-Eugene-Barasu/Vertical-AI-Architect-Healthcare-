import { useEffect, useState } from "react";
import axios from "axios";

interface Overview {
  total_organizations: number;
  active_organizations: number;
  plan_breakdown: Record<string, number>;
  estimated_mrr: number;
  estimated_arr: number;
}

interface Org {
  org_id: string;
  name: string;
  email: string;
  plan: string;
  status: string;
  created_at: string;
}

export default function AdminPortal() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [orgs, setOrgs] = useState<Org[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    Promise.all([
      axios.get("/api/admin/overview"),
      axios.get("/api/admin/organizations"),
    ]).then(([o, orgsRes]) => {
      setOverview(o.data);
      setOrgs(orgsRes.data.organizations);
    }).finally(() => setLoading(false));
  }, []);

  const updateStatus = async (org_id: string, status: string) => {
    await axios.put(`/api/admin/organizations/${org_id}/status`, { status });
    setOrgs((prev) => prev.map((o) => o.org_id === org_id ? { ...o, status } : o));
  };

  const updatePlan = async (org_id: string, plan: string) => {
    await axios.put(`/api/admin/organizations/${org_id}/plan`, { plan });
    setOrgs((prev) => prev.map((o) => o.org_id === org_id ? { ...o, plan } : o));
  };

  const filtered = orgs.filter((o) =>
    o.name?.toLowerCase().includes(search.toLowerCase()) ||
    o.email?.toLowerCase().includes(search.toLowerCase())
  );

  const statusColor = (s: string) => s === "active" ? "#38a169" : s === "suspended" ? "#dd6b20" : "#e53e3e";
  const planColor = (p: string) => p === "enterprise" ? "#805ad5" : p === "growth" ? "#2b6cb0" : "#718096";

  if (loading) return <div className="loading">Loading admin portal...</div>;

  return (
    <div className="admin-portal">
      <div className="admin-header">
        <h1>⚙️ Super Admin Portal</h1>
        <p>Platform-wide management for MediMind AI</p>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="admin-overview">
          {[
            { label: "Total Organizations", value: overview.total_organizations, icon: "🏥", color: "#2b6cb0" },
            { label: "Active Organizations", value: overview.active_organizations, icon: "✅", color: "#38a169" },
            { label: "Monthly Recurring Revenue", value: `$${overview.estimated_mrr.toLocaleString()}`, icon: "💰", color: "#805ad5" },
            { label: "Annual Recurring Revenue", value: `$${overview.estimated_arr.toLocaleString()}`, icon: "📈", color: "#dd6b20" },
          ].map((card) => (
            <div key={card.label} className="admin-stat-card" style={{ borderTop: `4px solid ${card.color}` }}>
              <span className="admin-stat-icon">{card.icon}</span>
              <strong style={{ color: card.color }}>{card.value}</strong>
              <span>{card.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Plan Breakdown */}
      {overview && (
        <div className="panel" style={{ marginBottom: "1.5rem" }}>
          <h3 style={{ marginBottom: "1rem" }}>Plan Distribution</h3>
          <div className="plan-breakdown">
            {Object.entries(overview.plan_breakdown).map(([plan, count]) => (
              <div key={plan} className="plan-bar-item">
                <span style={{ color: planColor(plan), fontWeight: 700, textTransform: "capitalize" }}>{plan}</span>
                <div className="plan-bar-track">
                  <div className="plan-bar-fill" style={{
                    width: `${overview.total_organizations ? (count / overview.total_organizations) * 100 : 0}%`,
                    background: planColor(plan)
                  }} />
                </div>
                <span>{count} orgs</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Organizations Table */}
      <div className="panel">
        <div className="admin-table-header">
          <h3>Organizations ({filtered.length})</h3>
          <input
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="admin-search"
          />
        </div>
        <div className="admin-table-wrapper">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Organization</th>
                <th>Email</th>
                <th>Plan</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((org) => (
                <tr key={org.org_id}>
                  <td><strong>{org.name}</strong></td>
                  <td>{org.email}</td>
                  <td>
                    <select
                      value={org.plan}
                      onChange={(e) => updatePlan(org.org_id, e.target.value)}
                      className="admin-select"
                      style={{ color: planColor(org.plan) }}
                    >
                      <option value="starter">Starter</option>
                      <option value="growth">Growth</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                  </td>
                  <td>
                    <span className="status-pill" style={{ background: statusColor(org.status) + "20", color: statusColor(org.status) }}>
                      {org.status}
                    </span>
                  </td>
                  <td>{org.created_at?.slice(0, 10)}</td>
                  <td>
                    <div className="admin-actions">
                      {org.status === "active"
                        ? <button className="action-btn suspend" onClick={() => updateStatus(org.org_id, "suspended")}>Suspend</button>
                        : <button className="action-btn activate" onClick={() => updateStatus(org.org_id, "active")}>Activate</button>
                      }
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
