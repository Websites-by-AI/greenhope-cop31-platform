/**
 * GreenHope COP31 — CRM Export API (Cloudflare Pages Function)
 * GET /api/download/crm?format=csv|json
 */

const PIPELINE_STAGES = [
  "Not Started", "Pack Ready", "Draft Auto-Filled", "Human Approved",
  "Submitted", "Meeting Booked", "Due Diligence / Partnered",
];

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
    var defaultStage = meta.knowledge_pack_slug ? "Pack Ready" : "Not Started";
    records[iid] = {
      investor_id: iid, stage: defaultStage, owner: "GreenHope Team",
      cop31_venue_or_channel: "COP31 Partner / Ecosystem Track", target_date: "2026-11-20",
      next_action: "Review " + meta.name + " COP31 mandate (" + meta.relationship_status + ") and decide outreach sequence.",
      notes: "", submitted_docs_count: 0, last_updated_utc: now,
    };
  }
  crmStore = { version: "1.0", stages: PIPELINE_STAGES, updated_at_utc: now, total_entities: Object.keys(records).length, records: records };
  return crmStore;
}

function csvEsc(v) {
  var s = String(v ?? "");
  if (s.includes(",") || s.includes('"') || s.includes("\\n")) {
    return '"' + s.replace(/"/g, '""') + '"';
  }
  return s;
}

export async function onRequest(context) {
  var url = new URL(context.request.url);
  var format = url.searchParams.get("format") || "json";
  var data = ensureInit();

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

  var headers = { "Access-Control-Allow-Origin": "*" };

  if (format === "csv") {
    var fields = ["investor_id","name","relationship_status","priority_tier","ai_rag_priority","stage","owner",
      "target_date","cop31_venue_or_channel","next_action","submitted_docs_count","notes","last_updated_utc"];
    var csv = fields.join(",") + "\n";
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      csv += fields.map(function(f) { return csvEsc(it[f]); }).join(",") + "\n";
    }
    headers["Content-Type"] = "text/csv; charset=utf-8";
    headers["Content-Disposition"] = 'attachment; filename="cop31_investor_crm_pipeline.csv"';
    return new Response(csv, { status: 200, headers: headers });
  } else {
    headers["Content-Type"] = "application/json; charset=utf-8";
    headers["Content-Disposition"] = 'attachment; filename="cop31_investor_crm_pipeline.json"';
    return new Response(JSON.stringify(data, null, 2), { status: 200, headers: headers });
  }
}
