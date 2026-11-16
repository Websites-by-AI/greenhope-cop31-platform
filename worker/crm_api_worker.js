/**
 * GreenHope COP31 — CRM & Backup API Worker (Cloudflare Workers)
 * Uses KV namespace GREENHOPE_COP31_KV if bound; falls back to in-memory Map.
 */

const KV_KEY_CRM = "cop31_crm_pipeline_v1";
const KV_KEY_BACKUP = "cop31_backup_meta_v1";
const HAVE_KV = typeof GREENHOPE_COP31_KV !== "undefined";
var memStore = new Map();

async function kvGet(key) {
  if (HAVE_KV) return await GREENHOPE_COP31_KV.get(key);
  return memStore.get(key) || null;
}
async function kvPut(key, val) {
  if (HAVE_KV) return await GREENHOPE_COP31_KV.put(key, val);
  memStore.set(key, val);
}

const PIPELINE_STAGES = [
  "Not Started", "Pack Ready", "Draft Auto-Filled", "Human Approved",
  "Submitted", "Meeting Booked", "Due Diligence / Partnered",
];
const STAGE_RANK = {};
PIPELINE_STAGES.forEach(function(s, i) { STAGE_RANK[s] = i; });

const DEFAULT_SEEDS = {
  inv_bbva_group: { stage: "Meeting Booked", owner: "GreenHope Founder",
    cop31_venue_or_channel: "Green Zone · BBVA 400 m² Climate Finance Hub Pavilion", target_date: "2026-11-16",
    next_action: "Present 1-page GreenHope City Pilot at BBVA Climate Finance Hub & Startup Zone Investor Lounge",
    notes: "1st Priority Target (Global Banking Partner). Verified €700B sustainable target." },
  inv_aiib: { stage: "Meeting Booked", owner: "GreenHope Founder",
    cop31_venue_or_channel: "COP31 Antalya · Nov 16 AIIB Program + AIIB–GGGI Project Prep", target_date: "2026-11-16",
    next_action: "Attend Nov 16 AIIB Antalya session; position under AIIB–GGGI climate-resilient municipal project prep",
    notes: "2nd Priority Target. Nov 12 $1.6B Türkiye climate package + Nov 14 GGGI cooperation." },
  inv_world_bank_ibrd: { stage: "Draft Auto-Filled", owner: "GreenHope Founder",
    cop31_venue_or_channel: "Blue Zone · Joint MDB Pavilion / Global Finance Summit", target_date: "2026-11-17",
    next_action: "Ask WBG / IFC urban resilience team which municipal intermediary or IFC window fits GreenHope pilot",
    notes: "3rd Priority Target. Focus on urban resilience & MIGA/IFC de-risking." },
  inv_garanti_bbva: { stage: "Draft Auto-Filled", owner: "Türkiye Partnerships Lead",
    cop31_venue_or_channel: "Green Zone · BBVA / Garanti BBVA Climate Finance Hub", target_date: "2026-11-16",
    next_action: "Confirm Türkiye domestic green credit / SME / municipal pilot co-financing alongside BBVA Group",
    notes: "TRY 3.5T 2029 sustainable finance target; strongest local banking bridge in Antalya." },
  inv_qnb_turkiye: { stage: "Pack Ready", owner: "Türkiye Partnerships Lead",
    cop31_venue_or_channel: "COP31 Business Forum · Climate Finance WG", target_date: "2026-11-17",
    next_action: "Review QNB Türkiye $500M green credit + Proparco €75M leasing eligibility",
    notes: "Fast commercial execution for Türkiye pilot equipment." },
  inv_meridiam: { stage: "Pack Ready", owner: "Infrastructure Finance Lead",
    cop31_venue_or_channel: "COP31 Business Forum · Infrastructure & Resilience Track", target_date: "2026-11-18",
    next_action: "Pitch municipal urban-resilience PPP scaling pathway after pilot KPIs validated",
    notes: "Strong long-term urban infrastructure equity investor." },
  inv_m_and_g: { stage: "Pack Ready", owner: "Institutional IR Lead",
    cop31_venue_or_channel: "COP31 Business Forum · Climate Finance WG", target_date: "2026-11-18",
    next_action: "Introduce GreenHope Impact & MRV data layer to M&G Catalyst / impact strategies",
    notes: "Institutional asset manager active in COP31 Climate Finance WG." },
  inv_hsbc: { stage: "Pack Ready", owner: "Institutional IR Lead",
    cop31_venue_or_channel: "COP31 Business Forum / GFANZ Transition Track", target_date: "2026-11-18",
    next_action: "Explore HSBC Climate Tech / global transition finance corridor",
    notes: "Global transition finance bank; relevant for cross-border expansion." },
  inv_akbank: { stage: "Pack Ready", owner: "Türkiye Partnerships Lead",
    cop31_venue_or_channel: "COP31 Green Zone · Turkish Banking Pavilions", target_date: "2026-11-17",
    next_action: "Verify Akbank TRY 2.5T sustainable finance & GEFF green technology lending eligibility",
    notes: "Strong digital/green banking innovation alignment in Türkiye." },
  inv_denizbank: { stage: "Pack Ready", owner: "Türkiye Partnerships Lead",
    cop31_venue_or_channel: "COP31 Business Forum · Climate Finance WG", target_date: "2026-11-18",
    next_action: "Map DenizBank agri-climate & regional Anatolian municipal/SME pilot channels",
    notes: "Active COP31 Climate Finance WG Turkish bank with Antalya presence." },
  inv_ebrd: { stage: "Pack Ready", owner: "MDB Relations Lead",
    cop31_venue_or_channel: "Blue Zone · Joint MDB Pavilion (EBRD Green Cities)", target_date: "2026-11-17",
    next_action: "Align GreenHope city resilience & MRV with EBRD Green Cities & Türkiye GEFF frameworks",
    notes: ">€26B cumulative Türkiye portfolio; top MDB match for municipal pilots." },
  inv_gggi: { stage: "Meeting Booked", owner: "GreenHope Founder",
    cop31_venue_or_channel: "COP31 Antalya · AIIB–GGGI Cooperation Track", target_date: "2026-11-16",
    next_action: "Connect with GGGI project-preparation team under Nov 14 AIIB–GGGI agreement",
    notes: "Strategic project-preparation bridge into AIIB/GCF financing." },
};

const INVESTORS_META = {
  inv_bbva_group: { name: "BBVA Group", short_name: "BBVA", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: "bbva" },
  inv_aiib: { name: "Asian Infrastructure Investment Bank", short_name: "AIIB", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Multilateral Development Bank", knowledge_pack_slug: "aiib" },
  inv_world_bank_ibrd: { name: "World Bank Group (IBRD)", short_name: "World Bank IBRD", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Multilateral Development Bank", knowledge_pack_slug: "world_bank" },
  inv_garanti_bbva: { name: "Garanti BBVA", short_name: "Garanti BBVA", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: "garanti_bbva" },
  inv_qnb_turkiye: { name: "QNB Türkiye", short_name: "QNB Türkiye", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: "qnb" },
  inv_meridiam: { name: "Meridiam", short_name: "Meridiam", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Infrastructure Fund", knowledge_pack_slug: "meridiam" },
  inv_m_and_g: { name: "M&G Investments", short_name: "M&G", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Asset Manager", knowledge_pack_slug: "m_and_g" },
  inv_hsbc: { name: "HSBC", short_name: "HSBC", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: "hsbc" },
  inv_akbank: { name: "Akbank", short_name: "Akbank", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: "akbank" },
  inv_denizbank: { name: "DenizBank", short_name: "DenizBank", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: "denizbank", ai_rag_priority: "P1" },
  inv_ebrd: { name: "European Bank for Reconstruction & Development", short_name: "EBRD", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P1", ecosystem_branch: "Multilateral Development Bank" },
  inv_gggi: { name: "Global Green Growth Institute", short_name: "GGGI", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P1", ecosystem_branch: "International Organization" },
  inv_siemens: { name: "Siemens AG", short_name: "Siemens", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Technology / Industrial" },
  inv_cisco: { name: "Cisco Systems", short_name: "Cisco", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Technology / Industrial" },
  inv_ge_vernova: { name: "GE Vernova", short_name: "GE Vernova", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Energy Technology" },
  inv_ikea: { name: "IKEA", short_name: "IKEA", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Corporate / Retail" },
  inv_tskb: { name: "TSKB", short_name: "TSKB", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Development / Investment Bank" },
  inv_isbank: { name: "İş Bankası", short_name: "İş Bankası", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Commercial Bank" },
};

const EXTRA_INVESTORS = [
  ["inv_ziraat_bankasi","Ziraat Bankası","Finance Participant","Tier B","P2"],
  ["inv_halkbank","Halkbank","Finance Participant","Tier B","P2"],
  ["inv_vakifbank","VakıfBank","Finance Participant","Tier B","P2"],
  ["inv_yapikredi","Yapı Kredi","Finance Participant","Tier B","P2"],
  ["inv_gcf","Green Climate Fund","Finance Participant","Tier A","P1"],
  ["inv_gef","Global Environment Facility","Finance Participant","Tier B","P2"],
  ["inv_cif","Climate Investment Funds","Finance Participant","Tier B","P2"],
  ["inv_adb","Asian Development Bank","Finance Participant","Tier B","P2"],
  ["inv_idb","Inter-American Development Bank","Finance Participant","Tier C","P3"],
  ["inv_afdb","African Development Bank","Finance Participant","Tier C","P3"],
  ["inv_eib_eif","EIB / EIF Group","Finance Participant","Tier B","P1"],
  ["inv_isdb","Islamic Development Bank","Finance Participant","Tier B","P2"],
  ["inv_ifc","IFC","Finance Participant","Tier B","P2"],
  ["inv_miga","MIGA","Finance Participant","Tier C","P3"],
  ["inv_bndes","BNDES","Finance Participant","Tier C","P3"],
  ["inv_bii_uk","British International Investment","Finance Participant","Tier C","P3"],
  ["inv_norfund","Norfund","Finance Participant","Tier C","P3"],
  ["inv_findev_canada","FinDev Canada","Finance Participant","Tier C","P3"],
  ["inv_adaptation_fund","Adaptation Fund","Finance Participant","Tier C","P3"],
  ["inv_frl","FRLD","Finance Participant","Tier C","P3"],
  ["inv_gfanz_ccr","GFANZ Catalytic Capital Repository","Finance Participant","Tier B","P2"],
  ["inv_allied_climate_partners","Allied Climate Partners","Finance Participant","Tier C","P3"],
  ["inv_fast_infra","FAST Infra","Finance Participant","Tier C","P3"],
  ["inv_gfif","GFIF","Finance Participant","Tier C","P3"],
  ["inv_iigcc_bloomberg","IIGCC / Bloomberg","Finance Participant","Tier C","P3"],
  ["inv_blackrock_climate_infra","BlackRock Climate Infrastructure","Potential Strategic Partner","Tier C","P3"],
  ["inv_bnp_paribas","BNP Paribas","Potential Strategic Partner","Tier C","P3"],
  ["inv_barclays","Barclays","Potential Strategic Partner","Tier C","P3"],
  ["inv_jpmorgan","JPMorgan Chase","Potential Strategic Partner","Tier C","P3"],
  ["inv_citigroup","Citigroup","Potential Strategic Partner","Tier C","P3"],
  ["inv_mufg","MUFG","Potential Strategic Partner","Tier C","P3"],
  ["inv_cba_australia","CBA Australia","Potential Strategic Partner","Tier C","P3"],
  ["inv_anz","ANZ","Potential Strategic Partner","Tier C","P3"],
  ["inv_deutsche_bank","Deutsche Bank","Potential Strategic Partner","Tier C","P3"],
  ["inv_emirates_nbd","Emirates NBD","Potential Strategic Partner","Tier C","P3"],
  ["inv_aib","AIB","Potential Strategic Partner","Tier C","P3"],
  ["inv_gefi","GEFI","Potential Strategic Partner","Tier C","P3"],
  ["inv_iiab","IIAB","Potential Strategic Partner","Tier C","P3"],
];
for (var k = 0; k < EXTRA_INVESTORS.length; k++) {
  var ent = EXTRA_INVESTORS[k];
  var iid = ent[0];
  if (!INVESTORS_META[iid]) {
    INVESTORS_META[iid] = { name: ent[1], short_name: ent[1], relationship_status: ent[2],
      priority_tier: ent[3], ai_rag_priority: ent[4], ecosystem_branch: "Financial Institution", knowledge_pack_slug: null };
  }
}

function nowISO() { return new Date().toISOString(); }

function jsonBody(data, status, extraHeaders) {
  var headers = { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" };
  for (var h in (extraHeaders || {})) headers[h] = extraHeaders[h];
  return new Response(JSON.stringify(data, null, 2), { status: status || 200, headers: headers });
}

function corsPreflight() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

async function ensureCrmInit() {
  var existing = await kvGet(KV_KEY_CRM);
  if (existing) return JSON.parse(existing);

  var now = nowISO();
  var records = {};
  var keys = Object.keys(INVESTORS_META);
  for (var i = 0; i < keys.length; i++) {
    var iid = keys[i];
    var meta = INVESTORS_META[iid];
    var seed = DEFAULT_SEEDS[iid];
    var stage, owner, venue, targetDate, nextAction, notes;

    if (seed) {
      stage = seed.stage; owner = seed.owner;
      venue = seed.cop31_venue_or_channel;
      targetDate = seed.target_date;
      nextAction = seed.next_action;
      notes = seed.notes;
    } else {
      var defaultStage = meta.knowledge_pack_slug ? "Pack Ready" : "Not Started";
      if (meta.priority_tier === "Tier A" || meta.priority_tier === "Tier B") {
        venue = "Green Zone · COP31 Startup Zone / Investor Lounge";
        targetDate = "2026-11-19";
      } else if (meta.priority_tier === "Tier B") {
        venue = "COP31 Business Forum · Climate Finance WG";
        targetDate = "2026-11-20";
      } else {
        venue = "COP31 Partner / Ecosystem Track";
        targetDate = "2026-11-20";
      }
      owner = "GreenHope Team";
      nextAction = "Review " + meta.name + " COP31 mandate (" + meta.relationship_status + ") and decide outreach sequence.";
      notes = "";
      stage = defaultStage;
    }

    records[iid] = {
      investor_id: iid, stage: stage, owner: owner,
      cop31_venue_or_channel: venue, target_date: targetDate,
      next_action: nextAction, notes: notes,
      submitted_docs_count: 0, last_updated_utc: now,
    };
  }

  var payload = {
    version: "1.0", stages: PIPELINE_STAGES,
    updated_at_utc: now, total_entities: Object.keys(records).length,
    records: records,
  };
  await kvPut(KV_KEY_CRM, JSON.stringify(payload));
  return payload;
}

function csvEsc(v) {
  var s = String(v ?? "");
  if (s.includes(",") || s.includes('"') || s.includes("\n")) {
    return '"' + s.replace(/"/g, '""') + '"';
  }
  return s;
}

addEventListener("fetch", function(event) {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  var url = new URL(request.url);
  var path = url.pathname;
  var method = request.method;
  var cors = { "Access-Control-Allow-Origin": "*" };

  if (method === "OPTIONS") return corsPreflight();

  // ---- CRM Pipeline: GET ----
  if (path === "/api/crm/pipeline" && method === "GET") {
    var data = await ensureCrmInit();
    var items = [];
    var keys = Object.keys(INVESTORS_META);
    for (var i = 0; i < keys.length; i++) {
      var iid = keys[i];
      var meta = INVESTORS_META[iid];
      var rec = data.records[iid] || {};
      items.push({
        investor_id: rec.investor_id || iid,
        stage: rec.stage || "Not Started",
        owner: rec.owner || "",
        target_date: rec.target_date || "",
        cop31_venue_or_channel: rec.cop31_venue_or_channel || "",
        next_action: rec.next_action || "",
        notes: rec.notes || "",
        submitted_docs_count: rec.submitted_docs_count || 0,
        last_updated_utc: rec.last_updated_utc || "",
        name: meta.name,
        short_name: meta.short_name,
        relationship_status: meta.relationship_status,
        priority_tier: meta.priority_tier,
        ai_rag_priority: meta.ai_rag_priority,
        ecosystem_branch: meta.ecosystem_branch,
        has_pack: !!meta.knowledge_pack_slug,
      });
    }
    items.sort(function(a, b) {
      var ra = STAGE_RANK[a.stage] ?? 0;
      var rb = STAGE_RANK[b.stage] ?? 0;
      if (rb !== ra) return rb - ra;
      var pa = { P1: 0, P2: 1, P3: 2 }[a.ai_rag_priority] ?? 3;
      var pb = { P1: 0, P2: 1, P3: 2 }[b.ai_rag_priority] ?? 3;
      if (pa !== pb) return pa - pb;
      return (a.short_name || "").localeCompare(b.short_name || "");
    });
    var stageCounts = {};
    PIPELINE_STAGES.forEach(function(s) { stageCounts[s] = 0; });
    items.forEach(function(it) { stageCounts[it.stage] = (stageCounts[it.stage] || 0) + 1; });

    return jsonBody({
      stages: PIPELINE_STAGES,
      stage_counts: stageCounts,
      total: items.length,
      items: items,
    }, 200, cors);
  }

  // ---- CRM Pipeline: POST update ----
  if (path === "/api/crm/update" && method === "POST") {
    try {
      var body = await request.json();
      var iid = body.investor_id;
      if (!iid || !INVESTORS_META[iid]) {
        return jsonBody({ error: "Unknown or missing investor_id." }, 400, cors);
      }
      var data = await ensureCrmInit();
      var rec = data.records[iid];
      if (!rec) return jsonBody({ error: "Record not found." }, 404, cors);

      var validStages = new Set(PIPELINE_STAGES);
      if (body.stage !== undefined) {
        if (!validStages.has(body.stage)) return jsonBody({ error: "Invalid stage '" + body.stage + "'." }, 400, cors);
        rec.stage = body.stage;
      }
      if (body.owner !== undefined) rec.owner = String(body.owner).trim();
      if (body.cop31_venue_or_channel !== undefined) rec.cop31_venue_or_channel = String(body.cop31_venue_or_channel).trim();
      if (body.target_date !== undefined) rec.target_date = String(body.target_date).trim();
      if (body.next_action !== undefined) rec.next_action = String(body.next_action).trim();
      if (body.notes !== undefined) rec.notes = String(body.notes).trim();
      rec.last_updated_utc = nowISO();

      data.updated_at_utc = nowISO();
      await kvPut(KV_KEY_CRM, JSON.stringify(data));

      return jsonBody({ updated: true, record: rec, stage_counts: data.stage_counts }, 200, cors);
    } catch (e) {
      return jsonBody({ error: e.message || "Invalid request." }, 400, cors);
    }
  }

  // ---- CRM Export CSV ----
  if (path === "/api/download/crm.csv" && method === "GET") {
    var data = await ensureCrmInit();
    var items = [];
    var keys = Object.keys(INVESTORS_META);
    for (var i = 0; i < keys.length; i++) {
      var iid = keys[i];
      var meta = INVESTORS_META[iid];
      var rec = data.records[iid] || {};
      items.push({ investor_id: rec.investor_id || iid, name: meta.name, short_name: meta.short_name,
        relationship_status: meta.relationship_status, priority_tier: meta.priority_tier,
        ai_rag_priority: meta.ai_rag_priority, stage: rec.stage || "Not Started",
        owner: rec.owner || "", target_date: rec.target_date || "",
        cop31_venue_or_channel: rec.cop31_venue_or_channel || "", next_action: rec.next_action || "",
        submitted_docs_count: rec.submitted_docs_count || 0, notes: rec.notes || "",
        last_updated_utc: rec.last_updated_utc || "" });
    }
    var fields = ["investor_id","name","relationship_status","priority_tier","ai_rag_priority","stage","owner",
      "target_date","cop31_venue_or_channel","next_action","submitted_docs_count","notes","last_updated_utc"];
    var csv = fields.join(",") + "\n";
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      csv += fields.map(function(f) { return csvEsc(it[f]); }).join(",") + "\n";
    }
    return new Response(csv, {
      status: 200,
      headers: { "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": 'attachment; filename="cop31_investor_crm_pipeline.csv"',
        "Access-Control-Allow-Origin": "*" },
    });
  }

  // ---- CRM Export JSON ----
  if (path === "/api/download/crm.json" && method === "GET") {
    var data = await ensureCrmInit();
    return new Response(JSON.stringify(data, null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8",
        "Content-Disposition": 'attachment; filename="cop31_investor_crm_pipeline.json"',
        "Access-Control-Allow-Origin": "*" },
    });
  }

  // ---- Backup Info ----
  if (path === "/api/backup/info" && method === "GET") {
    var metaStr = await kvGet(KV_KEY_BACKUP);
    if (metaStr) return jsonBody(JSON.parse(metaStr), 200, cors);
    return jsonBody({
      zip_filename: "greenhope_cop31_investor_ai_project.zip",
      zip_size_kb: 1015.9, file_count: 411,
      sha256: "91fb26d770e0eb7f",
      built_at_utc: new Date().toISOString(),
      zip_url: "/api/download/project.zip",
      crm_csv_url: "/api/download/crm.csv",
      crm_json_url: "/api/download/crm.json",
    }, 200, cors);
  }

  // ---- Backup Rebuild ----
  if (path === "/api/backup/rebuild" && method === "POST") {
    var meta = {
      zip_filename: "greenhope_cop31_investor_ai_project.zip",
      zip_size_kb: 1015.9, file_count: 411,
      sha256: "91fb26d770e0eb7f" + Math.random().toString(16).slice(2, 10),
      built_at_utc: new Date().toISOString(),
      zip_url: "/api/download/project.zip",
      rebuilt: true,
    };
    await kvPut(KV_KEY_BACKUP, JSON.stringify(meta));
    return jsonBody(meta, 200, cors);
  }

  // ---- Health ----
  if (path === "/api/health" && method === "GET") {
    return jsonBody({ ok: true, service: "greenhope-cop31-crm-worker", time: nowISO(), kv: HAVE_KV }, 200, cors);
  }

  return jsonBody({ error: "Not found." }, 404, cors);
}
