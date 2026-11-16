/**
 * GreenHope COP31 — CRM Pipeline API (Cloudflare Pages Function)
 * GET /api/crm/pipeline — list all investors with pipeline stages
 */

const PIPELINE_STAGES = [
  "Not Started", "Pack Ready", "Draft Auto-Filled", "Human Approved",
  "Submitted", "Meeting Booked", "Due Diligence / Partnered",
];
const STAGE_RANK = {};
PIPELINE_STAGES.forEach(function(s, i) { STAGE_RANK[s] = i; });

const DEFAULT_SEEDS = {
  inv_aiib: { stage: "Meeting Booked", owner: "GreenHope Founder", cop31_venue_or_channel: "COP31 Antalya · Nov 16 AIIB Program + AIIB–GGGI Project Prep", target_date: "2026-11-16", next_action: "Attend Nov 16 AIIB Antalya session; position under AIIB–GGGI climate-resilient municipal project prep", notes: "2nd Priority Target. Nov 12 $1.6B Türkiye climate package + Nov 14 GGGI cooperation." },
  inv_akbank: { stage: "Pack Ready", owner: "Türkiye Partnerships Lead", cop31_venue_or_channel: "COP31 Green Zone · Turkish Banking Pavilions", target_date: "2026-11-17", next_action: "Verify Akbank TRY 2.5T sustainable finance & GEFF green technology lending eligibility", notes: "Strong digital/green banking innovation alignment in Türkiye." },
  inv_bbva_group: { stage: "Meeting Booked", owner: "GreenHope Founder", cop31_venue_or_channel: "Green Zone · BBVA 400 m² Climate Finance Hub Pavilion", target_date: "2026-11-16", next_action: "Present 1-page GreenHope City Pilot at BBVA Climate Finance Hub & Startup Zone Investor Lounge", notes: "1st Priority Target (Global Banking Partner). Verified €700B sustainable target." },
  inv_denizbank: { stage: "Pack Ready", owner: "Türkiye Partnerships Lead", cop31_venue_or_channel: "COP31 Business Forum · Climate Finance WG", target_date: "2026-11-18", next_action: "Map DenizBank agri-climate & regional Anatolian municipal/SME pilot channels", notes: "Active COP31 Climate Finance WG Turkish bank with Antalya presence." },
  inv_ebrd: { stage: "Pack Ready", owner: "MDB Relations Lead", cop31_venue_or_channel: "Blue Zone · Joint MDB Pavilion (EBRD Green Cities)", target_date: "2026-11-17", next_action: "Align GreenHope city resilience & MRV with EBRD Green Cities & Türkiye GEFF frameworks", notes: ">€26B cumulative Türkiye portfolio; top MDB match for municipal pilots." },
  inv_garanti_bbva: { stage: "Draft Auto-Filled", owner: "Türkiye Partnerships Lead", cop31_venue_or_channel: "Green Zone · BBVA / Garanti BBVA Climate Finance Hub", target_date: "2026-11-16", next_action: "Confirm Türkiye domestic green credit / SME / municipal pilot co-financing alongside BBVA Group", notes: "TRY 3.5T 2029 sustainable finance target; strongest local banking bridge in Antalya." },
  inv_gggi: { stage: "Meeting Booked", owner: "GreenHope Founder", cop31_venue_or_channel: "COP31 Antalya · AIIB–GGGI Cooperation Track", target_date: "2026-11-16", next_action: "Connect with GGGI project-preparation team under Nov 14 AIIB–GGGI agreement", notes: "Strategic project-preparation bridge into AIIB/GCF financing." },
  inv_hsbc: { stage: "Pack Ready", owner: "Institutional IR Lead", cop31_venue_or_channel: "COP31 Business Forum / GFANZ Transition Track", target_date: "2026-11-18", next_action: "Explore HSBC Climate Tech / global transition finance corridor", notes: "Global transition finance bank; relevant for cross-border expansion." },
  inv_m_and_g: { stage: "Pack Ready", owner: "Institutional IR Lead", cop31_venue_or_channel: "COP31 Business Forum · Climate Finance WG", target_date: "2026-11-18", next_action: "Introduce GreenHope Impact & MRV data layer to M&G Catalyst / impact strategies", notes: "Institutional asset manager active in COP31 Climate Finance WG." },
  inv_meridiam: { stage: "Pack Ready", owner: "Infrastructure Finance Lead", cop31_venue_or_channel: "COP31 Business Forum · Infrastructure & Resilience Track", target_date: "2026-11-18", next_action: "Pitch municipal urban-resilience PPP scaling pathway after pilot KPIs validated", notes: "Strong long-term urban infrastructure equity investor." },
  inv_qnb_turkiye: { stage: "Pack Ready", owner: "Türkiye Partnerships Lead", cop31_venue_or_channel: "COP31 Business Forum · Climate Finance WG", target_date: "2026-11-17", next_action: "Review QNB Türkiye $500M green credit + Proparco €75M leasing eligibility", notes: "Fast commercial execution for Türkiye pilot equipment." },
  inv_world_bank_ibrd: { stage: "Draft Auto-Filled", owner: "GreenHope Founder", cop31_venue_or_channel: "Blue Zone · Joint MDB Pavilion / Global Finance Summit", target_date: "2026-11-17", next_action: "Ask WBG / IFC urban resilience team which municipal intermediary or IFC window fits GreenHope pilot", notes: "3rd Priority Target. Focus on urban resilience & MIGA/IFC de-risking." },
};

const INVESTORS_META = {
  inv_adaptation_fund: { name: "Adaptation Fund (AF)", short_name: "Adaptation Fund", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Climate Fund", knowledge_pack_slug: null },
  inv_adb: { name: "Asian Development Bank (ADB)", short_name: "Asian Development Bank", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_afdb: { name: "African Development Bank Group (AfDB)", short_name: "African Development Bank Group", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_aib: { name: "AIB (Allied Irish Banks)", short_name: "AIB", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_aiib: { name: "Asian Infrastructure Investment Bank (AIIB)", short_name: "Asian Infrastructure Investment Bank", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Development Bank", knowledge_pack_slug: aiib },
  inv_akbank: { name: "Akbank", short_name: "Akbank", relationship_status: "Investor Confirmed", priority_tier: "Tier B", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: akbank },
  inv_allied_climate_partners: { name: "Allied Climate Partners (ACP)", short_name: "Allied Climate Partners", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_anz: { name: "ANZ (Australia and New Zealand Banking Group)", short_name: "ANZ", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_barclays: { name: "Barclays (Sustainable & Transition Finance)", short_name: "Barclays", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_bbva_group: { name: "BBVA Group", short_name: "BBVA Group", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Financial Institution", knowledge_pack_slug: bbva },
  inv_bii_uk: { name: "British International Investment (BII — UK)", short_name: "British International Investment", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_blackrock_climate_infra: { name: "BlackRock (Climate Infrastructure & Transition Investing)", short_name: "BlackRock", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_bndes: { name: "BNDES (Brazilian Development Bank)", short_name: "BNDES", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_bnp_paribas: { name: "BNP Paribas", short_name: "BNP Paribas", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_cba_australia: { name: "Commonwealth Bank of Australia (CommBank)", short_name: "Commonwealth Bank of Australia", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_cif: { name: "Climate Investment Funds (CIF / Clean Technology Fund)", short_name: "Climate Investment Funds", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Climate Fund", knowledge_pack_slug: null },
  inv_cisco: { name: "Cisco", short_name: "Cisco", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Technology / Industrial", knowledge_pack_slug: null },
  inv_citigroup: { name: "Citigroup (Citi Sustainable Finance & Transition)", short_name: "Citigroup", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_denizbank: { name: "DenizBank", short_name: "DenizBank", relationship_status: "Investor Confirmed", priority_tier: "Tier B", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: denizbank },
  inv_deutsche_bank: { name: "Deutsche Bank", short_name: "Deutsche Bank", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_ebrd: { name: "European Bank for Reconstruction and Development (EBRD)", short_name: "European Bank for Reconstruction and Development", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P1", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_eib_eif: { name: "European Investment Bank (EIB) & European Investment Fund (EIF)", short_name: "European Investment Bank", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_emirates_nbd: { name: "Emirates NBD", short_name: "Emirates NBD", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_fast_infra: { name: "FAST-Infra Group", short_name: "FAST-Infra Group", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_findev_canada: { name: "FinDev Canada", short_name: "FinDev Canada", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_frld: { name: "Fund for Responding to Loss and Damage (FRLD)", short_name: "Fund for Responding to Loss and Damage", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Climate Fund", knowledge_pack_slug: null },
  inv_garanti_bbva: { name: "Garanti BBVA", short_name: "Garanti BBVA", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Financial Institution", knowledge_pack_slug: garanti_bbva },
  inv_gcf: { name: "Green Climate Fund (GCF)", short_name: "Green Climate Fund", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Climate Fund", knowledge_pack_slug: null },
  inv_ge_vernova: { name: "GE Vernova", short_name: "GE Vernova", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Technology / Industrial", knowledge_pack_slug: null },
  inv_gef: { name: "Global Environment Facility (GEF — incl. LDCF & SCCF)", short_name: "Global Environment Facility", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Climate Fund", knowledge_pack_slug: null },
  inv_gefi: { name: "Global Ethical Finance Initiative (GEFI)", short_name: "Global Ethical Finance Initiative", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_gfanz_ccr: { name: "GFANZ / Catalytic Capital Repository (GCBC)", short_name: "GFANZ", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_gfif: { name: "GFIF (Global Finance & Investment Forum at COP31)", short_name: "GFIF", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_gggi: { name: "Global Green Growth Institute (GGGI)", short_name: "Global Green Growth Institute", relationship_status: "Potential Strategic Partner", priority_tier: "Tier C", ai_rag_priority: "P1", ecosystem_branch: "International Organization", knowledge_pack_slug: null },
  inv_halkbank: { name: "Halkbank", short_name: "Halkbank", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_hsbc: { name: "HSBC", short_name: "HSBC", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Financial Institution", knowledge_pack_slug: hsbc },
  inv_idb: { name: "Inter-American Development Bank (IDB / IDB Invest)", short_name: "Inter-American Development Bank", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_ifc: { name: "International Finance Corporation (IFC)", short_name: "International Finance Corporation", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_iiab: { name: "Impact Investing Advisory Board (EYDK / Türkiye Impact Network)", short_name: "Impact Investing Advisory Board", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_iigcc_bloomberg: { name: "IIGCC & Bloomberg Philanthropies Climate Finance Network", short_name: "IIGCC", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_ikea: { name: "IKEA (Ingka Group / Ingka Investments)", short_name: "IKEA", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Technology / Industrial", knowledge_pack_slug: null },
  inv_ilbank: { name: "İLBANK (İller Bankası — Türkiye Municipal Development Bank)", short_name: "İLBANK", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_invest_tr: { name: "Investment and Finance Office of the Presidency of Türkiye (Invest in Türkiye)", short_name: "Investment and Finance Office of the Presidency of Türkiye", relationship_status: "Potential Strategic Partner", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_isbank: { name: "Türkiye İş Bankası (İşbank)", short_name: "Türkiye İş Bankası", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_isdb: { name: "Islamic Development Bank (IsDB)", short_name: "Islamic Development Bank", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_jpmorgan_chase: { name: "JPMorgan Chase (Green Economy & Sustainable Finance)", short_name: "JPMorgan Chase", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_just_climate: { name: "Just Climate (Generation Investment Management)", short_name: "Just Climate", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_kfw: { name: "KfW Development Bank (Germany)", short_name: "KfW Development Bank", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_lloyds: { name: "Lloyds Banking Group", short_name: "Lloyds Banking Group", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_m_and_g: { name: "M&G (M&G Investments / Catalyst)", short_name: "M&G", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Financial Institution", knowledge_pack_slug: m_and_g },
  inv_meridiam: { name: "Meridiam", short_name: "Meridiam", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Financial Institution", knowledge_pack_slug: meridiam },
  inv_mufg: { name: "Mitsubishi UFJ Financial Group (MUFG)", short_name: "Mitsubishi UFJ Financial Group", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_norfund: { name: "Norfund (Norwegian Investment Fund / Climate Investment Fund)", short_name: "Norfund", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Climate Fund", knowledge_pack_slug: null },
  inv_proparco_afd: { name: "AFD Group / Proparco (France)", short_name: "AFD Group", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_qnb_turkiye: { name: "QNB Türkiye & QNB Leasing", short_name: "QNB Türkiye", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Financial Institution", knowledge_pack_slug: qnb },
  inv_sap: { name: "SAP", short_name: "SAP", relationship_status: "Potential Strategic Partner", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Technology / Industrial", knowledge_pack_slug: null },
  inv_siemens: { name: "Siemens (Siemens Energy / Smart Infrastructure)", short_name: "Siemens", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P3", ecosystem_branch: "Technology / Industrial", knowledge_pack_slug: null },
  inv_standard_bank: { name: "Standard Bank Group", short_name: "Standard Bank Group", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_standard_chartered: { name: "Standard Chartered Bank", short_name: "Standard Chartered Bank", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_tskb: { name: "TSKB (Industrial Development Bank of Türkiye)", short_name: "TSKB", relationship_status: "COP31 Supporter", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Development Bank", knowledge_pack_slug: null },
  inv_turk_eximbank: { name: "Turk Eximbank", short_name: "Turk Eximbank", relationship_status: "Investor Confirmed", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_vakifbank: { name: "VakıfBank", short_name: "VakıfBank", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_world_bank_ibrd: { name: "World Bank Group (IBRD / IDA)", short_name: "World Bank Group", relationship_status: "Investor Confirmed", priority_tier: "Tier A", ai_rag_priority: "P1", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: world_bank },
  inv_yapi_kredi: { name: "Yapı Kredi", short_name: "Yapı Kredi", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
  inv_ziraat_bankasi: { name: "Ziraat Bankası", short_name: "Ziraat Bankası", relationship_status: "Finance Participant", priority_tier: "Tier B", ai_rag_priority: "P2", ecosystem_branch: "Commercial Bank", knowledge_pack_slug: null },
  inv_zurich_turkiye: { name: "Zurich Life & Pension Türkiye (Zurich Group)", short_name: "Zurich Life", relationship_status: "Finance Participant", priority_tier: "Tier C", ai_rag_priority: "P2", ecosystem_branch: "Financial Institution", knowledge_pack_slug: null },
};

// In-memory store (persists within function isolate)
var crmStore = null;

function nowISO() { return new Date().toISOString(); }

function ensureInit() {
  if (crmStore) return crmStore;
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

  crmStore = {
    version: "1.0", stages: PIPELINE_STAGES,
    updated_at_utc: now, total_entities: Object.keys(records).length,
    records: records,
  };
  return crmStore;
}

function jsonBody(data, status, extraHeaders) {
  var headers = { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" };
  for (var h in (extraHeaders || {})) headers[h] = extraHeaders[h];
  return new Response(JSON.stringify(data, null, 2), { status: status || 200, headers: headers });
}

export async function onRequest(context) {
  var data = ensureInit();
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
  }, 200);
}
