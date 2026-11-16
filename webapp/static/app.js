/* GreenHope × COP31 Antalya Investor Intelligence & KAG/RAG Frontend (Relative API URLs Only) */

const state = {
  user: null,
  overview: null,
  investors: [],
  packs: [],
  crm: { stages: [], stage_counts: {}, items: [] },
  backup: null,
  activePackSlug: null,
  activePackData: null,
  activeDraft: null,
  kgData: null,
};

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

function esc(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function statusPill(status) {
  if (status === "Investor Confirmed") return `<span class="pill pill-emerald">Investor Confirmed</span>`;
  if (status === "Finance Participant") return `<span class="pill pill-blue">Finance Participant</span>`;
  if (status === "COP31 Supporter") return `<span class="pill pill-rose">COP31 Supporter · Non-Investor</span>`;
  return `<span class="pill pill-purple">Potential Strategic Partner</span>`;
}

function secPill(level) {
  if (level === "LEVEL_1_PUBLIC") return `<span class="pill pill-emerald">LEVEL 1 · PUBLIC</span>`;
  if (level === "LEVEL_2_INTERNAL") return `<span class="pill pill-amber">LEVEL 2 · INTERNAL</span>`;
  if (level === "LEVEL_3_CONFIDENTIAL") return `<span class="pill pill-rose">LEVEL 3 · CONFIDENTIAL</span>`;
  return `<span class="pill pill-rose">LEVEL 4 · RESTRICTED</span>`;
}

/* ==================== AUTH & BOOTSTRAP ==================== */
async function initApp() {
  bindEvents();
  try {
    const me = await apiFetch("/api/me");
    if (me.downloads?.zip_size_kb) {
      document.getElementById("zip-size-badge").textContent = `${me.downloads.zip_size_kb} KB`;
    }
    if (me.authenticated) {
      enterDashboard(me.user);
    }
  } catch (err) {
    console.error(err);
  }
}

async function loginDemo(role = "ADMIN") {
  const errBox = document.getElementById("login-error");
  errBox.classList.add("hidden");
  try {
    const res = await apiFetch("/api/login", {
      method: "POST",
      body: JSON.stringify({ mode: "demo", role }),
    });
    enterDashboard(res.user);
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  }
}

async function loginCredentials(evt) {
  evt.preventDefault();
  const errBox = document.getElementById("login-error");
  errBox.classList.add("hidden");
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  try {
    const res = await apiFetch("/api/login", {
      method: "POST",
      body: JSON.stringify({ mode: "credentials", username, password }),
    });
    enterDashboard(res.user);
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  }
}

async function enterDashboard(user) {
  state.user = user;
  document.getElementById("login-view").classList.add("hidden");
  document.getElementById("app-view").classList.remove("hidden");
  document.getElementById("user-name-label").textContent = user.display_name;
  document.getElementById("user-role-badge").textContent = user.role;

  await Promise.all([loadOverview(), loadInvestors(), loadCRM(), loadMaster(), loadSecurity(), loadBackupInfo()]);
  populateSelects();
  renderPacksSidebar();
  if (state.packs.length) {
    await selectPack(state.packs[0].investor_id);
  }
  await loadKnowledgeGraph();
  await runCompare("inv_bbva_group", "inv_ziraat_bankasi");
  await runAgentDraft("inv_bbva_group");
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tabId));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("active", p.id === `tab-${tabId}`));
}

/* ==================== TAB 1: OVERVIEW ==================== */
async function loadOverview() {
  const data = await apiFetch("/api/overview");
  state.overview = data;
  state.packs = data.packs_index || [];

  // Immediate COP31 Alerts (Nov 16 AIIB + Startup Zone)
  document.getElementById("alerts-grid").innerHTML = data.immediate_alerts
    .map(
      (a) => `
      <div class="live-alert-card">
        <span class="pill pill-amber">${esc(a.tag)}</span>
        <h3>${esc(a.title)}</h3>
        <p>${esc(a.summary)}</p>
        <div class="live-alert-actions">
          <button class="btn btn-primary btn-xs" onclick="openEntityAndAgent('${esc(a.target_investor_id)}')">Draft GreenHope Pitch →</button>
          <a class="btn btn-outline btn-xs" href="${esc(a.source_url)}" target="_blank" rel="noopener">Official COP31 Source ↗</a>
        </div>
      </div>`
    )
    .join("");

  const k = data.kpis;
  const kpis = [
    ["Verified COP31 Entities", k.total_entities, `${k.investor_confirmed} Investor Confirmed`],
    ["Finance Participants", k.finance_participant, "COP31 Business Forum WG"],
    ["Supporters / Partners", k.cop31_supporter + k.strategic_partner, "Strictly separated from funders"],
    ["P1 Knowledge Packs", k.knowledge_packs, "13 structured files per pack"],
    ["Central KAG + RAG", `${k.kg_nodes} / ${k.rag_chunks}`, `${k.kg_edges} KG edges · scoped chunks`],
    ["AES-256-GCM Vault", k.audit_chain_valid ? "VERIFIED" : "ALERT", `${k.audit_entries} audit entries · Merkle OK`],
  ];
  document.getElementById("kpi-grid").innerHTML = kpis
    .map(
      ([label, val, sub]) => `
      <div class="kpi-card">
        <div class="kpi-label">${esc(label)}</div>
        <div class="kpi-value">${esc(val)}</div>
        <div class="kpi-sub">${esc(sub)}</div>
      </div>`
    )
    .join("");

  document.getElementById("top3-grid").innerHTML = data.top3_attack_briefs
    .map(
      (b) => `
      <div class="attack-card">
        <span class="pill pill-emerald">${esc(b.rank)}</span>
        <h3>${esc(b.title)}</h3>
        <div class="muted small"><strong>${esc(b.headline)}</strong></div>
        <div class="pathway-box"><strong>Pitch Logic:</strong> ${esc(b.pathway)}</div>
        <p class="small">${esc(b.why)}</p>
        <div class="inline-actions">
          <button class="btn btn-primary btn-xs" onclick="openEntityAndAgent('${esc(b.investor_id)}')">Run Application Agent</button>
          <button class="btn btn-secondary btn-xs" onclick="openPackTab('${esc(b.investor_id)}')">Open Knowledge Pack</button>
        </div>
      </div>`
    )
    .join("");

  // Tier A / B / C Attack Sequence
  document.getElementById("tiers-container").innerHTML = Object.entries(data.tiers)
    .map(
      ([tierName, list]) => `
      <div class="tier-block">
        <h4>${esc(tierName)} <span class="muted">(${list.length})</span></h4>
        <div class="chip-cloud">
          ${list
            .map(
              (item) =>
                `<button class="entity-chip ${item.has_pack ? "has-pack" : ""}" onclick="openEntityModal('${esc(item.investor_id)}')" title="${esc(item.fit_notes)}">${esc(item.short_name)} ${item.has_pack ? "★" : ""}</button>`
            )
            .join("")}
        </div>
      </div>`
    )
    .join("");

  // Ecosystem Tree
  document.getElementById("ecosystem-tree-container").innerHTML = Object.entries(data.ecosystem_tree)
    .map(
      ([branch, list]) => `
      <div class="tier-block">
        <h4>${esc(branch)} <span class="muted">(${list.length})</span></h4>
        <div class="chip-cloud">
          ${list
            .map(
              (item) =>
                `<button class="entity-chip ${item.has_pack ? "has-pack" : ""}" onclick="openEntityModal('${esc(item.investor_id)}')">${esc(item.short_name)}</button>`
            )
            .join("")}
        </div>
      </div>`
    )
    .join("");
}

/* ==================== TAB 2: 66-ENTITY DATABASE ==================== */
async function loadInvestors() {
  const data = await apiFetch("/api/investors");
  state.investors = data.investors || [];
  renderInvestorsTable();
}

function renderInvestorsTable() {
  const q = document.getElementById("inv-search").value.trim().toLowerCase();
  const st = document.getElementById("filter-status").value;
  const tier = document.getElementById("filter-tier").value;
  const prio = document.getElementById("filter-priority").value;
  const packOnly = document.getElementById("filter-pack-only").checked;

  const filtered = state.investors.filter((inv) => {
    if (st && inv.relationship_status !== st) return false;
    if (tier && inv.priority_tier !== tier) return false;
    if (prio && inv.ai_rag_priority !== prio) return false;
    if (packOnly && !inv.knowledge_pack_slug) return false;
    if (q) {
      const hay = `${inv.name} ${inv.short_name} ${inv.cop31_antalya_role} ${inv.cop31_verified_2026_commitment} ${inv.greenhope_fit_notes} ${inv.ecosystem_branch} ${inv.target_sectors.join(" ")}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  document.getElementById("inv-count-label").textContent = `Showing ${filtered.length} of ${state.investors.length} verified COP31 entities`;
  document.getElementById("investors-tbody").innerHTML = filtered
    .map(
      (inv) => `
      <tr>
        <td>
          <strong>${esc(inv.name)}</strong><br/>
          <span class="muted small">${esc(inv.hq_country)} · <code>${esc(inv.investor_id)}</code></span>
          ${inv.knowledge_pack_slug ? `<br/><span class="pill pill-emerald">★ 13-File Pack: investors/${esc(inv.knowledge_pack_slug)}/</span>` : ""}
        </td>
        <td>${statusPill(inv.relationship_status)}</td>
        <td>
          <span class="pill ${inv.ai_rag_priority === "P1" ? "pill-rose" : inv.ai_rag_priority === "P2" ? "pill-amber" : "pill-blue"}">${esc(inv.ai_rag_priority)}</span>
          <div class="muted small" style="margin-top:4px">${esc(inv.priority_tier.split("—")[0])}</div>
        </td>
        <td><span class="fit-score">${inv.greenhope_fit_score}</span><div class="muted small">/ 100</div></td>
        <td>
          <div class="small"><strong>${esc(inv.ecosystem_branch)}</strong></div>
          <div class="muted small">${esc(inv.financing_instruments.slice(0, 2).join(", "))}</div>
        </td>
        <td>
          <div class="small">${esc(inv.greenhope_fit_notes)}</div>
          <div class="muted small" style="margin-top:4px">${esc(inv.cop31_verified_2026_commitment.slice(0, 145))}${inv.cop31_verified_2026_commitment.length > 145 ? "..." : ""}</div>
        </td>
        <td>
          <div class="inline-actions">
            <button class="btn btn-secondary btn-xs" onclick="openEntityModal('${esc(inv.investor_id)}')">Inspect</button>
            <button class="btn btn-primary btn-xs" onclick="openEntityAndAgent('${esc(inv.investor_id)}')">Auto-Fill</button>
            <button class="btn btn-outline btn-xs" onclick="openCRMForEntity('${esc(inv.investor_id)}')">CRM</button>
          </div>
        </td>
      </tr>`
    )
    .join("");
}

/* ==================== TAB 3: 10 P1 KNOWLEDGE PACKS ==================== */
function renderPacksSidebar() {
  document.getElementById("packs-list").innerHTML = state.packs
    .map(
      (p) => `
      <button class="pack-item" data-pack-inv="${esc(p.investor_id)}" onclick="selectPack('${esc(p.investor_id)}')">
        <div class="pack-item-title">${esc(p.name)}</div>
        <div class="pack-item-sub"><code>investors/${esc(p.slug)}/</code> · ${esc(p.relationship_status)} · ${p.verified_claims_count} verified claims</div>
      </button>`
    )
    .join("");
}

async function selectPack(investorId) {
  document.querySelectorAll(".pack-item").forEach((el) => el.classList.toggle("active", el.dataset.packInv === investorId));
  const data = await apiFetch(`/api/investors/${encodeURIComponent(investorId)}/pack`);
  state.activePackData = data;
  const inv = data.investor;

  document.getElementById("pack-header").innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">
      <div>
        <h3 style="margin:0 0 4px">${esc(inv.name)}</h3>
        <div class="inline-actions">
          ${statusPill(inv.relationship_status)}
          <span class="pill pill-amber">${esc(inv.priority_tier)}</span>
          <span class="pill pill-blue">Fit Score: ${data.fit.greenhope_fit_score}/100</span>
        </div>
      </div>
      <div class="inline-actions">
        <button class="btn btn-primary btn-sm" onclick="openEntityAndAgent('${esc(inv.investor_id)}')">Draft Application →</button>
        <a class="btn btn-outline btn-sm" href="${esc(inv.application_portal_url)}" target="_blank" rel="noopener">Official Portal ↗</a>
      </div>
    </div>`;

  const fileNames = [...Object.keys(data.pack_files), "evidence/verified_claims.json"];
  document.getElementById("pack-file-tabs").innerHTML = fileNames
    .map((fn, idx) => `<button class="file-tab ${idx === 0 ? "active" : ""}" onclick="showPackFile('${esc(fn)}', this)">${esc(fn)}</button>`)
    .join("");
  if (fileNames.length) showPackFile(fileNames[0]);
}

function showPackFile(fileName, btnEl) {
  if (btnEl) {
    document.querySelectorAll(".file-tab").forEach((b) => b.classList.remove("active"));
    btnEl.classList.add("active");
  }
  const box = document.getElementById("pack-file-content");
  if (fileName === "evidence/verified_claims.json") {
    box.textContent = JSON.stringify({ claims: state.activePackData.verified_claims }, null, 2);
  } else {
    const val = state.activePackData.pack_files[fileName];
    box.textContent = typeof val === "string" ? val : JSON.stringify(val, null, 2);
  }
}

window.openPackTab = async function (investorId) {
  switchTab("packs");
  await selectPack(investorId);
};

/* ==================== TAB 4: CENTRAL KAG + SCOPED RAG ==================== */
async function loadKnowledgeGraph() {
  const data = await apiFetch("/api/kag/graph");
  state.kgData = data;
  renderKnowledgeGraphSVG(data);
}

function renderKnowledgeGraphSVG(data, activeInvestorId = null) {
  const domains = data.nodes.filter((n) => n.group === "domain");
  const investors = data.nodes.filter((n) => n.group === "investor");

  const width = 1080;
  const height = 430;
  const pos = { GreenHope: { x: 115, y: height / 2 } };

  domains.forEach((d, i) => {
    pos[d.id] = { x: 430, y: 48 + i * ((height - 96) / Math.max(1, domains.length - 1)) };
  });
  investors.forEach((inv, i) => {
    pos[inv.id] = { x: 890, y: 34 + i * ((height - 68) / Math.max(1, investors.length - 1)) };
  });

  const activeDomains = new Set();
  if (activeInvestorId) {
    data.edges.forEach((e) => {
      if (e.target === activeInvestorId) activeDomains.add(e.source);
    });
  }

  const linesSvg = data.edges
    .map((e) => {
      const a = pos[e.source];
      const b = pos[e.target];
      if (!a || !b) return "";
      const highlight = !activeInvestorId || e.target === activeInvestorId || (e.source === "GreenHope" && activeDomains.has(e.target));
      const stroke = highlight ? (e.source === "GreenHope" ? "#10b981" : "#38bdf8") : "#1e3a52";
      const opacity = highlight ? 0.85 : 0.16;
      return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="${stroke}" stroke-opacity="${opacity}" stroke-width="${highlight ? 2.1 : 1}" />`;
    })
    .join("");

  const coreNode = `
    <g>
      <circle cx="${pos.GreenHope.x}" cy="${pos.GreenHope.y}" r="48" fill="#065f46" stroke="#10b981" stroke-width="3"/>
      <text x="${pos.GreenHope.x}" y="${pos.GreenHope.y - 4}" text-anchor="middle" fill="#ecfdf5" font-weight="800" font-size="14">GreenHope</text>
      <text x="${pos.GreenHope.x}" y="${pos.GreenHope.y + 14}" text-anchor="middle" fill="#a7f3d0" font-size="10">City Pilot Core</text>
    </g>`;

  const domainNodes = domains
    .map((d) => {
      const p = pos[d.id];
      const hi = !activeInvestorId || activeDomains.has(d.id);
      return `
        <g opacity="${hi ? 1 : 0.35}">
          <rect x="${p.x - 76}" y="${p.y - 16}" width="152" height="32" rx="16" fill="#0f2940" stroke="${hi ? "#10b981" : "#244058"}" stroke-width="1.6"/>
          <text x="${p.x}" y="${p.y + 4}" text-anchor="middle" fill="#e0f2fe" font-weight="700" font-size="12">${esc(d.label)}</text>
        </g>`;
    })
    .join("");

  const invNodes = investors
    .map((inv) => {
      const p = pos[inv.id];
      const hi = !activeInvestorId || inv.id === activeInvestorId;
      return `
        <g style="cursor:pointer" opacity="${hi ? 1 : 0.35}" onclick="highlightKGInvestor('${esc(inv.id)}')">
          <rect x="${p.x - 102}" y="${p.y - 15}" width="204" height="30" rx="8" fill="${inv.id === activeInvestorId ? "#0d9488" : "#14283a"}" stroke="${hi ? "#38bdf8" : "#244058"}" stroke-width="1.6"/>
          <text x="${p.x}" y="${p.y + 4}" text-anchor="middle" fill="#f8fafc" font-weight="700" font-size="12">${esc(inv.label)} (${esc(inv.priority)})</text>
        </g>`;
    })
    .join("");

  document.getElementById("kg-svg-wrap").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" width="100%" style="max-height:430px;display:block;">
      ${linesSvg}${coreNode}${domainNodes}${invNodes}
    </svg>`;
}

window.highlightKGInvestor = function (investorId) {
  renderKnowledgeGraphSVG(state.kgData, investorId);
  const inv = state.investors.find((i) => i.investor_id === investorId);
  if (!inv) return;
  document.getElementById("kg-selected-info").innerHTML = `
    <strong>${esc(inv.name)}</strong> (${statusPill(inv.relationship_status)}) —
    Aligned GreenHope KG Domains: <code>${esc((inv.aligned_domains || []).join(", "))}</code> ·
    Fit Score: <strong>${inv.greenhope_fit_score}/100</strong>
    <button class="btn btn-xs btn-secondary" style="margin-left:10px" onclick="renderKnowledgeGraphSVG(state.kgData, null)">Reset Graph</button>`;
};

function populateSelects() {
  const opts = state.investors
    .map((i) => `<option value="${esc(i.investor_id)}">${esc(i.short_name)} — ${esc(i.relationship_status)} (${esc(i.ai_rag_priority)})</option>`)
    .join("");
  document.getElementById("rag-scope").innerHTML = `<option value="">ALL 66 COP31 ENTITIES (Global Scope)</option>${opts}`;
  document.getElementById("cmp-a").innerHTML = opts;
  document.getElementById("cmp-b").innerHTML = opts;
  document.getElementById("agent-investor").innerHTML = opts;

  document.getElementById("cmp-a").value = "inv_bbva_group";
  document.getElementById("cmp-b").value = "inv_ziraat_bankasi";
  document.getElementById("agent-investor").value = "inv_bbva_group";
}

async function runRagQuery() {
  const query = document.getElementById("rag-query").value.trim();
  const investor_id = document.getElementById("rag-scope").value || null;
  const res = await apiFetch("/api/rag/query", {
    method: "POST",
    body: JSON.stringify({ query, investor_id, top_k: 5 }),
  });

  document.getElementById("rag-results").innerHTML =
    `<div class="small muted">Scope: <strong>${esc(res.scope)}</strong> · ${res.results.length} grounded evidence chunks retrieved</div>` +
    res.results
      .map(
        (r) => `
      <div class="rag-hit">
        <div style="display:flex;justify-content:space-between;gap:8px;margin-bottom:4px;">
          <code>${esc(r.source_file)}</code>
          <span class="pill pill-emerald">Score ${r.score} · Conf ${r.confidence}</span>
        </div>
        <div class="small">${esc(r.excerpt)}</div>
        <div class="small" style="margin-top:5px"><a href="${esc(r.url)}" target="_blank" rel="noopener">Verify Source ↗</a></div>
      </div>`
      )
      .join("");
}

async function runCompare(aId, bId) {
  const invA = aId || document.getElementById("cmp-a").value;
  const invB = bId || document.getElementById("cmp-b").value;
  const res = await apiFetch("/api/kag/compare", {
    method: "POST",
    body: JSON.stringify({ investor_a: invA, investor_b: invB }),
  });

  document.getElementById("compare-results").innerHTML = `
    <div style="margin-bottom:10px;">
      <span class="pill pill-emerald">Recommended Higher-Priority Target: ${esc(res.recommended_name)}</span>
    </div>
    <div class="split-2" style="grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
      <div class="tier-block">
        <h4>${esc(res.investor_a.short_name)} — <span class="fit-score">${res.investor_a.greenhope_fit_score}/100</span></h4>
        <div>${statusPill(res.investor_a.relationship_status)}</div>
        <div class="muted small" style="margin-top:6px">KG Domains: ${esc(res.investor_a.aligned_domains.join(", "))}</div>
      </div>
      <div class="tier-block">
        <h4>${esc(res.investor_b.short_name)} — <span class="fit-score">${res.investor_b.greenhope_fit_score}/100</span></h4>
        <div>${statusPill(res.investor_b.relationship_status)}</div>
        <div class="muted small" style="margin-top:6px">KG Domains: ${esc(res.investor_b.aligned_domains.join(", "))}</div>
      </div>
    </div>
    <ul style="margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px;">
      ${res.evidence_based_reasons.map((r) => `<li class="small">${esc(r).replaceAll(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}</li>`).join("")}
    </ul>`;
}

/* ==================== TAB 5: APPLICATION AGENT ==================== */
async function runAgentDraft(investorId = null, overrides = {}) {
  const targetId = investorId || document.getElementById("agent-investor").value;
  document.getElementById("agent-investor").value = targetId;
  document.getElementById("agent-export-status").classList.add("hidden");

  const draft = await apiFetch("/api/agent/draft", {
    method: "POST",
    body: JSON.stringify({ investor_id: targetId, overrides }),
  });
  state.activeDraft = draft;
  loadCRM().catch(() => {});

  const warnEl = document.getElementById("agent-warning");
  if (draft.supporter_warning) {
    warnEl.textContent = draft.supporter_warning;
    warnEl.classList.remove("hidden");
  } else {
    warnEl.classList.add("hidden");
  }

  document.getElementById("agent-summary").innerHTML = `
    <span class="pill pill-blue">${esc(draft.investor_name)}</span>
    ${statusPill(draft.relationship_status)}
    <span class="pill pill-emerald">Ready: ${draft.ready_count}</span>
    <span class="pill pill-amber">Missing (ASK_USER): ${draft.missing_count}</span>
    <span class="pill pill-rose">IP Blocked: ${draft.blocked_ip_count}</span>`;

  renderAgentFields();
}

function renderAgentFields() {
  const draft = state.activeDraft;
  document.getElementById("agent-fields").innerHTML = draft.fields
    .map((f, idx) => {
      const cls =
        f.status === "BLOCKED_BY_IP_SECURITY"
          ? "status-blocked"
          : f.status === "MISSING_INFORMATION"
          ? "status-missing"
          : "status-ready";

      let bodyHtml = "";
      if (f.status === "BLOCKED_BY_IP_SECURITY") {
        bodyHtml = `
          <div class="alert alert-danger" style="margin:6px 0 0">
            <strong>🛡️ BLOCKED BY 4-TIER IP SECURITY:</strong> Proprietary algorithms / unpublished IP / credentials are NEVER auto-submitted. Share only under executed NDA.
          </div>`;
      } else if (f.status === "MISSING_INFORMATION") {
        bodyHtml = `
          <div style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.4);border-radius:8px;padding:10px;margin-top:6px;">
            <div class="small" style="color:#fcd34d;margin-bottom:6px;">
              <strong>ZERO-HALLUCINATION GUARD:</strong> <code>{"answer": null, "status": "MISSING_INFORMATION", "action": "ASK_USER"}</code>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
              <input type="text" id="missing-input-${idx}" placeholder="Enter verified ${esc(f.field)} (e.g., Pre-revenue / Pilot stage — USD 0 audited 2026)" style="flex:1;min-width:240px;" />
              <button class="btn btn-primary btn-xs" onclick="supplyMissingField('${esc(f.master_key)}', ${idx})">Save to GREENHOPE_MASTER &amp; Re-Draft</button>
            </div>
          </div>`;
      } else {
        bodyHtml = `
          <textarea class="agent-answer-box" oninput="updateDraftAnswer(${idx}, this.value)">${esc(f.answer)}</textarea>
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <span class="muted small">Source: ${esc(f.source)} · Conf: ${f.confidence} ${f.rag_citations.length ? `· Cited: ${esc(f.rag_citations.join(", "))}` : ""}</span>
            <label class="checkbox-inline" style="color:#6ee7b7;font-weight:700;">
              <input type="checkbox" ${f.approved ? "checked" : ""} onchange="toggleFieldApprove(${idx}, this.checked)" />
              Human Approved for Submission
            </label>
          </div>`;
      }

      return `
        <div class="agent-field-card ${cls}">
          <div class="agent-field-head">
            <div><strong>${esc(f.field)}</strong> <code style="margin-left:6px">${esc(f.field_id)}</code></div>
            <div class="inline-actions">
              ${secPill(f.security_level)}
              <span class="pill pill-blue">${esc(f.status)}</span>
            </div>
          </div>
          <div class="muted small">${esc(f.pipeline_trace)}</div>
          ${bodyHtml}
        </div>`;
    })
    .join("");
}

window.updateDraftAnswer = function (idx, val) {
  state.activeDraft.fields[idx].answer = val;
};
window.toggleFieldApprove = function (idx, checked) {
  state.activeDraft.fields[idx].approved = checked;
};
window.supplyMissingField = async function (masterKey, idx) {
  const val = document.getElementById(`missing-input-${idx}`).value.trim();
  if (!val) return;
  await apiFetch("/api/greenhope/master", {
    method: "POST",
    body: JSON.stringify({ key: masterKey, value: val }),
  });
  await loadMaster();
  await runAgentDraft(state.activeDraft.investor_id);
};

async function exportApprovedDraft() {
  const statusBox = document.getElementById("agent-export-status");
  statusBox.classList.add("hidden");
  try {
    const res = await apiFetch("/api/agent/export", {
      method: "POST",
      body: JSON.stringify({
        investor_id: state.activeDraft.investor_id,
        fields: state.activeDraft.fields,
      }),
    });
    statusBox.innerHTML = `<strong>✅ Human-Approved Application Packet Exported:</strong> <code>outputs/approved_submissions/${esc(res.filename)}</code> (${res.packet.approved_fields.length} approved fields; Level 3/4 confidential IP strictly excluded). CRM stage updated to <strong>Human Approved</strong>.`;
    statusBox.classList.remove("hidden");
    await Promise.all([loadSecurity(), loadCRM()]);
  } catch (err) {
    alert(err.message);
  }
}

window.openEntityAndAgent = async function (investorId) {
  closeModal();
  switchTab("agent");
  await runAgentDraft(investorId);
};

/* ==================== TAB 6: INVESTOR CRM PIPELINE ==================== */
async function loadCRM() {
  const data = await apiFetch("/api/crm/pipeline");
  state.crm = data;

  const sel = document.getElementById("crm-filter-stage");
  const prev = sel.value;
  sel.innerHTML = `<option value="">All Pipeline Stages (${data.total})</option>` +
    data.stages.map((s) => `<option value="${esc(s)}">${esc(s)} (${data.stage_counts[s] || 0})</option>`).join("");
  sel.value = prev;

  renderCRMStageCards();
  renderCRMTable();
}

function renderCRMStageCards() {
  const activeStage = document.getElementById("crm-filter-stage").value;
  document.getElementById("crm-stage-cards").innerHTML = state.crm.stages
    .map(
      (st) => `
      <button class="crm-stage-card ${activeStage === st ? "active" : ""}" type="button" onclick="toggleCRMStageFilter('${esc(st)}')">
        <div class="crm-stage-name">${esc(st)}</div>
        <div class="crm-stage-count">${state.crm.stage_counts[st] || 0}</div>
      </button>`
    )
    .join("");
}

window.toggleCRMStageFilter = function (stage) {
  const sel = document.getElementById("crm-filter-stage");
  sel.value = sel.value === stage ? "" : stage;
  renderCRMStageCards();
  renderCRMTable();
};

function renderCRMTable() {
  const q = document.getElementById("crm-search").value.trim().toLowerCase();
  const stageFilter = document.getElementById("crm-filter-stage").value;
  const prioFilter = document.getElementById("crm-filter-priority").value;

  const filtered = (state.crm.items || []).filter((item) => {
    if (stageFilter && item.stage !== stageFilter) return false;
    if (prioFilter && item.ai_rag_priority !== prioFilter) return false;
    if (q) {
      const hay = `${item.name} ${item.short_name} ${item.owner} ${item.cop31_venue_or_channel} ${item.next_action} ${item.notes} ${item.stage}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  document.getElementById("crm-count-label").textContent = `Showing ${filtered.length} of ${state.crm.total} tracked COP31 entities`;
  document.getElementById("crm-tbody").innerHTML = filtered
    .map(
      (item) => `
      <tr>
        <td>
          <strong>${esc(item.name)}</strong><br/>
          <div class="inline-actions" style="margin-top:4px;">
            ${statusPill(item.relationship_status)}
            <span class="pill ${item.ai_rag_priority === "P1" ? "pill-rose" : item.ai_rag_priority === "P2" ? "pill-amber" : "pill-blue"}">${esc(item.ai_rag_priority)}</span>
            ${item.submitted_docs_count > 0 ? `<span class="pill pill-emerald">${item.submitted_docs_count} Approved Packet(s)</span>` : ""}
          </div>
        </td>
        <td>
          <select class="stage-select" onchange="quickUpdateCRMStage('${esc(item.investor_id)}', this.value)">
            ${state.crm.stages.map((s) => `<option value="${esc(s)}" ${s === item.stage ? "selected" : ""}>${esc(s)}</option>`).join("")}
          </select>
        </td>
        <td>
          <div class="small"><strong>${esc(item.target_date || "TBD")}</strong></div>
          <div class="muted small">${esc(item.owner)}</div>
        </td>
        <td class="small">${esc(item.cop31_venue_or_channel)}</td>
        <td>
          <div class="small"><strong>Next:</strong> ${esc(item.next_action)}</div>
          <div class="muted small" style="margin-top:3px">${esc((item.notes || "").slice(0, 140))}${(item.notes || "").length > 140 ? "..." : ""}</div>
        </td>
        <td>
          <div class="inline-actions">
            <button class="btn btn-secondary btn-xs" onclick="openCRMEditModal('${esc(item.investor_id)}')">Edit Notes</button>
            <button class="btn btn-primary btn-xs" onclick="openEntityAndAgent('${esc(item.investor_id)}')">Auto-Fill</button>
          </div>
        </td>
      </tr>`
    )
    .join("");
}

window.quickUpdateCRMStage = async function (investorId, newStage) {
  await apiFetch("/api/crm/update", {
    method: "POST",
    body: JSON.stringify({ investor_id: investorId, stage: newStage }),
  });
  showCRMToast();
  await Promise.all([loadCRM(), loadSecurity()]);
};

function showCRMToast() {
  const el = document.getElementById("crm-save-toast");
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 2500);
}

window.openCRMForEntity = function (investorId) {
  closeModal();
  switchTab("crm");
  openCRMEditModal(investorId);
};

window.openCRMEditModal = function (investorId) {
  const item = (state.crm.items || []).find((x) => x.investor_id === investorId);
  if (!item) return;
  document.getElementById("modal-title").textContent = `CRM Pipeline — ${item.name}`;
  document.getElementById("modal-body").innerHTML = `
    <div class="stack-form">
      <div class="inline-actions">
        ${statusPill(item.relationship_status)}
        <span class="pill pill-amber">${esc(item.priority_tier)}</span>
      </div>
      <div class="split-2" style="grid-template-columns:1fr 1fr;gap:10px;">
        <div class="field-row">
          <label>Pipeline Stage</label>
          <select id="crm-edit-stage">
            ${state.crm.stages.map((s) => `<option value="${esc(s)}" ${s === item.stage ? "selected" : ""}>${esc(s)}</option>`).join("")}
          </select>
        </div>
        <div class="field-row">
          <label>Target COP31 Date</label>
          <input id="crm-edit-date" type="text" value="${esc(item.target_date)}" placeholder="YYYY-MM-DD" />
        </div>
      </div>
      <div class="split-2" style="grid-template-columns:1fr 1fr;gap:10px;">
        <div class="field-row">
          <label>Responsible Owner</label>
          <input id="crm-edit-owner" type="text" value="${esc(item.owner)}" />
        </div>
        <div class="field-row">
          <label>COP31 Venue / Channel</label>
          <input id="crm-edit-venue" type="text" value="${esc(item.cop31_venue_or_channel)}" />
        </div>
      </div>
      <div class="field-row">
        <label>Next Concrete Action</label>
        <textarea id="crm-edit-next" rows="2">${esc(item.next_action)}</textarea>
      </div>
      <div class="field-row">
        <label>Meeting &amp; Outreach Notes</label>
        <textarea id="crm-edit-notes" rows="3">${esc(item.notes)}</textarea>
      </div>
      <div class="inline-actions" style="justify-content:flex-end;margin-top:6px;">
        <button class="btn btn-secondary btn-sm" type="button" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary btn-sm" type="button" onclick="saveCRMEditModal('${esc(item.investor_id)}')">Save CRM Record</button>
      </div>
    </div>`;
  document.getElementById("entity-modal").classList.remove("hidden");
};

window.saveCRMEditModal = async function (investorId) {
  await apiFetch("/api/crm/update", {
    method: "POST",
    body: JSON.stringify({
      investor_id: investorId,
      stage: document.getElementById("crm-edit-stage").value,
      target_date: document.getElementById("crm-edit-date").value,
      owner: document.getElementById("crm-edit-owner").value,
      cop31_venue_or_channel: document.getElementById("crm-edit-venue").value,
      next_action: document.getElementById("crm-edit-next").value,
      notes: document.getElementById("crm-edit-notes").value,
    }),
  });
  closeModal();
  showCRMToast();
  await Promise.all([loadCRM(), loadSecurity()]);
};

/* ==================== BACKUP CENTER ==================== */
async function loadBackupInfo() {
  const info = await apiFetch("/api/backup/info");
  state.backup = info;
  renderBackupInfo(info);
}

function renderBackupInfo(info) {
  document.getElementById("zip-size-badge").textContent = `${info.zip_size_kb} KB`;
  document.getElementById("backup-info-view").innerHTML = `
    <div class="backup-stat">
      <div class="backup-stat-label">Archive Filename</div>
      <div class="backup-stat-val"><code>${esc(info.zip_filename)}</code></div>
    </div>
    <div class="backup-stat">
      <div class="backup-stat-label">Archive Size &amp; Files</div>
      <div class="backup-stat-val">${info.zip_size_kb} KB · ${info.file_count} files</div>
    </div>
    <div class="backup-stat">
      <div class="backup-stat-label">Last Built (UTC)</div>
      <div class="backup-stat-val">${esc(info.built_at_utc.replace("T", " ").slice(0, 19))}</div>
    </div>
    <div class="backup-stat">
      <div class="backup-stat-label">Backup Integrity SHA-256</div>
      <div class="backup-stat-val"><code>${esc(info.sha256.slice(0, 24))}…</code></div>
    </div>`;
}

async function rebuildBackupZip() {
  const btn = document.getElementById("btn-rebuild-zip");
  btn.disabled = true;
  btn.textContent = "Rebuilding ZIP...";
  try {
    const info = await apiFetch("/api/backup/rebuild", { method: "POST", body: "{}" });
    state.backup = info;
    renderBackupInfo(info);
    await loadSecurity();
    btn.textContent = "✓ Backup ZIP Updated!";
    setTimeout(() => {
      btn.textContent = "🔄 Rebuild Fresh Backup ZIP";
      btn.disabled = false;
    }, 2000);
  } catch (err) {
    alert(err.message);
    btn.textContent = "🔄 Rebuild Fresh Backup ZIP";
    btn.disabled = false;
  }
}

/* ==================== TAB 7: GREENHOPE_MASTER ==================== */
async function loadMaster() {
  const data = await apiFetch("/api/greenhope/master");
  const fields = data.canonical_fields || {};
  document.getElementById("master-fields-grid").innerHTML = Object.entries(fields)
    .map(([key, info]) => {
      const locked = info.classification === "LEVEL_4_RESTRICTED";
      return `
        <div class="master-card">
          <div class="master-card-head">
            <strong><code>${esc(key)}</code></strong>
            ${secPill(info.classification)}
          </div>
          <div class="muted small">Source: ${esc(info.source)} · Conf: ${info.confidence}</div>
          ${
            locked
              ? `<div class="alert alert-danger" style="margin:0;padding:8px 10px;">🔒 Locked Level 4 Restricted secret — never sent to AI or external forms.</div>`
              : `<textarea id="master-val-${esc(key)}" rows="2" placeholder="null (MISSING_INFORMATION -> triggers ASK_USER)">${esc(info.value ?? "")}</textarea>
                 <div style="display:flex;justify-content:flex-end;">
                   <button class="btn btn-secondary btn-xs" onclick="saveMasterField('${esc(key)}')">Save Verified Value</button>
                 </div>`
          }
        </div>`;
    })
    .join("");
}

window.saveMasterField = async function (key) {
  const val = document.getElementById(`master-val-${key}`).value.trim();
  await apiFetch("/api/greenhope/master", {
    method: "POST",
    body: JSON.stringify({ key, value: val || null }),
  });
  await loadMaster();
  if (state.activeDraft) {
    await runAgentDraft(state.activeDraft.investor_id);
  }
};

/* ==================== TAB 7: SECURITY VAULT & AUDIT ==================== */
async function loadSecurity() {
  const data = await apiFetch("/api/security/status");
  const m = data.vault_manifest;
  document.getElementById("vault-manifest-view").innerHTML = `
    <div class="tier-block">
      <div class="small"><strong>Cipher:</strong> <code>${esc(m.cipher)}</code> (${esc(m.crypto_backend)})</div>
      <div class="small" style="margin-top:6px"><strong>KDF:</strong> <code>${esc(m.kdf)}</code></div>
      <div class="small" style="margin-top:6px"><strong>Records Secured:</strong> ${m.record_count} verified COP31 entities</div>
      <div class="small" style="margin-top:6px"><strong>Merkle Root SHA-256:</strong><br/><code>${esc(m.merkle_root_sha256)}</code></div>
      <div class="small" style="margin-top:6px"><strong>Manifest HMAC-SHA256:</strong><br/><code>${esc(m.manifest_hmac_sha256)}</code></div>
    </div>`;

  document.getElementById("ip-tiers-view").innerHTML = Object.entries(data.ip_tiers)
    .map(
      ([tier, desc]) => `
      <div class="tier-block" style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
        ${secPill(tier)}
        <span class="small">${esc(desc)}</span>
      </div>`
    )
    .join("");

  document.getElementById("audit-chain-badge").textContent = data.audit_chain_valid
    ? `✓ Chain Verified (${data.audit_total_entries} entries)`
    : "⚠ Chain Tampered";

  document.getElementById("audit-tbody").innerHTML = (data.recent_audit_entries || [])
    .map(
      (e) => `
      <tr>
        <td>#${e.seq}</td>
        <td class="small">${esc(e.timestamp_utc.replace("T", " ").slice(0, 19))}</td>
        <td class="small"><strong>${esc(e.actor)}</strong><br/><span class="muted">${esc(e.role)}</span></td>
        <td><code>${esc(e.action)}</code></td>
        <td><span class="pill ${e.outcome === "SUCCESS" ? "pill-emerald" : "pill-rose"}">${esc(e.outcome)}</span></td>
        <td class="small">${esc(e.details)}</td>
        <td><code>${esc(e.entry_hash.slice(0, 16))}…</code></td>
      </tr>`
    )
    .join("");
}

async function runLiveVaultVerify() {
  const banner = document.getElementById("vault-verify-banner");
  const res = await apiFetch("/api/security/verify", { method: "POST", body: "{}" });
  banner.innerHTML = `✅ <strong>LIVE CRYPTOGRAPHIC CHECK PASSED:</strong> Decrypted &amp; Merkle-verified ${res.record_count} COP31 records (${esc(res.crypto_backend)}). Audit Chain Valid: ${res.audit_chain_valid} (${res.audit_entries} entries).`;
  banner.classList.remove("hidden");
  await loadSecurity();
}

/* ==================== ENTITY MODAL ==================== */
window.openEntityModal = async function (investorId) {
  const data = await apiFetch(`/api/investors/${encodeURIComponent(investorId)}/pack`);
  const inv = data.investor;
  document.getElementById("modal-title").textContent = inv.name;
  document.getElementById("modal-body").innerHTML = `
    <div class="inline-actions" style="margin-bottom:12px;">
      ${statusPill(inv.relationship_status)}
      <span class="pill pill-amber">${esc(inv.priority_tier)}</span>
      <span class="pill pill-blue">Priority ${esc(inv.ai_rag_priority)}</span>
      <span class="pill pill-emerald">GreenHope Fit ${data.fit.greenhope_fit_score}/100</span>
    </div>
    <div class="tier-block">
      <div class="small"><strong>COP31 Antalya 2026 Role:</strong> ${esc(inv.cop31_antalya_role)}</div>
      <div class="small" style="margin-top:6px"><strong>Verified Commitment:</strong> ${esc(inv.cop31_verified_2026_commitment)}</div>
      <div class="small" style="margin-top:6px"><strong>GreenHope Fit Strategy:</strong> ${esc(inv.greenhope_fit_notes)}</div>
      <div class="small" style="margin-top:6px"><strong>Financing Instruments:</strong> ${esc(inv.financing_instruments.join(", "))}</div>
      <div class="small" style="margin-top:6px"><strong>Typical Ticket Band:</strong> $${inv.typical_ticket_min_usd.toLocaleString()} – $${inv.typical_ticket_max_usd.toLocaleString()}</div>
      <div class="small" style="margin-top:6px"><strong>Aligned GreenHope KG Domains:</strong> <code>${esc(data.fit.aligned_domains.join(", "))}</code></div>
    </div>
    <h4 style="margin:12px 0 6px;">Verified Evidence Claims (${data.verified_claims.length})</h4>
    ${data.verified_claims
      .map(
        (c) => `
      <div class="rag-hit" style="margin-bottom:8px;">
        <div class="small">${esc(c.claim)}</div>
        <div class="muted small" style="margin-top:4px">${esc(c.source)} · Verified ${esc(c.date_verified)} · Conf ${c.confidence} · <a href="${esc(c.url)}" target="_blank" rel="noopener">Source ↗</a></div>
      </div>`
      )
      .join("")}
    <div class="inline-actions" style="margin-top:14px;">
      <button class="btn btn-primary btn-sm" onclick="openEntityAndAgent('${esc(inv.investor_id)}')">Draft GreenHope Application →</button>
      <button class="btn btn-secondary btn-sm" onclick="openCRMForEntity('${esc(inv.investor_id)}')">Track in CRM Pipeline</button>
      ${data.has_full_pack ? `<button class="btn btn-secondary btn-sm" onclick="closeModal();openPackTab('${esc(inv.investor_id)}')">Open 13-File Knowledge Pack</button>` : ""}
      <a class="btn btn-outline btn-sm" href="${esc(inv.application_portal_url)}" target="_blank" rel="noopener">Official Portal ↗</a>
    </div>`;
  document.getElementById("entity-modal").classList.remove("hidden");
};

window.closeModal = function () {
  document.getElementById("entity-modal").classList.add("hidden");
};

/* ==================== EVENT WIRING ==================== */
function bindEvents() {
  document.getElementById("btn-demo-login").addEventListener("click", () => loginDemo("ADMIN"));
  document.querySelectorAll("[data-demo-role]").forEach((btn) => {
    btn.addEventListener("click", () => loginDemo(btn.dataset.demoRole));
  });
  document.getElementById("login-form").addEventListener("submit", loginCredentials);
  document.getElementById("btn-logout").addEventListener("click", async () => {
    await apiFetch("/api/logout", { method: "POST" });
    document.getElementById("app-view").classList.add("hidden");
    document.getElementById("login-view").classList.remove("hidden");
  });

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  ["inv-search", "filter-status", "filter-tier", "filter-priority", "filter-pack-only"].forEach((id) => {
    document.getElementById(id).addEventListener("input", renderInvestorsTable);
    document.getElementById(id).addEventListener("change", renderInvestorsTable);
  });

  document.getElementById("btn-run-rag").addEventListener("click", runRagQuery);
  document.querySelectorAll(".rag-preset").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("rag-scope").value = btn.dataset.scope;
      document.getElementById("rag-query").value = btn.dataset.q;
      runRagQuery();
    });
  });

  document.getElementById("btn-run-compare").addEventListener("click", () => runCompare());
  document.getElementById("btn-agent-draft").addEventListener("click", () => runAgentDraft());
  document.getElementById("btn-agent-approve-all").addEventListener("click", () => {
    if (!state.activeDraft) return;
    state.activeDraft.fields.forEach((f) => {
      if (f.status === "ready_for_approval" || f.status === "requires_user_confirmation") {
        f.approved = true;
      }
    });
    renderAgentFields();
  });
  document.getElementById("btn-agent-export").addEventListener("click", exportApprovedDraft);
  document.querySelectorAll(".agent-preset").forEach((btn) => {
    btn.addEventListener("click", () => runAgentDraft(btn.dataset.inv));
  });

  document.getElementById("btn-verify-vault").addEventListener("click", runLiveVaultVerify);
  document.getElementById("btn-rebuild-zip").addEventListener("click", rebuildBackupZip);

  ["crm-search", "crm-filter-stage", "crm-filter-priority"].forEach((id) => {
    document.getElementById(id).addEventListener("input", () => {
      renderCRMStageCards();
      renderCRMTable();
    });
    document.getElementById(id).addEventListener("change", () => {
      renderCRMStageCards();
      renderCRMTable();
    });
  });
  document.getElementById("crm-clear-filters").addEventListener("click", () => {
    document.getElementById("crm-search").value = "";
    document.getElementById("crm-filter-stage").value = "";
    document.getElementById("crm-filter-priority").value = "";
    renderCRMStageCards();
    renderCRMTable();
  });

  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("entity-modal").addEventListener("click", (e) => {
    if (e.target.id === "entity-modal") closeModal();
  });
}

document.addEventListener("DOMContentLoaded", initApp);
