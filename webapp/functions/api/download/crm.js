/**
 * GreenHope COP31 — CRM Export API (Cloudflare Pages Function)
 * GET /api/download/crm?format=csv|json
 */

const PIPELINE_STAGES = [
  "Not Started", "Pack Ready", "Draft Auto-Filled", "Human Approved",
  "Submitted", "Meeting Booked", "Due Diligence / Partnered",
];
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
  if (s.includes(",") || s.includes('"') || s.includes("\n")) {
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
