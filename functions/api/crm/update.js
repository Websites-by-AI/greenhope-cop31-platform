/**
 * GreenHope COP31 — CRM Update API (Cloudflare Pages Function)
 * POST /api/crm/update — update a CRM record
 */

const PIPELINE_STAGES = [
  "Not Started", "Pack Ready", "Draft Auto-Filled", "Human Approved",
  "Submitted", "Meeting Booked", "Due Diligence / Partnered",
];
const STAGE_RANK = {};
PIPELINE_STAGES.forEach(function(s, i) { STAGE_RANK[s] = i; });

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

function jsonBody(data, status, extraHeaders) {
  var headers = { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" };
  for (var h in (extraHeaders || {})) headers[h] = extraHeaders[h];
  return new Response(JSON.stringify(data, null, 2), { status: status || 200, headers: headers });
}

function ensureInit() {
  if (crmStore) return crmStore;
  var now = nowISO();
  var records = {};
  var keys = Object.keys(INVESTORS_META);
  for (var i = 0; i < keys.length; i++) {
    var iid = keys[i];
    var meta = INVESTORS_META[iid];
    var defaultStage = meta.knowledge_pack_slug ? "Pack Ready" : "Not Started";
    var owner = "GreenHope Team";
    var venue = "COP31 Partner / Ecosystem Track";
    var targetDate = "2026-11-20";
    var nextAction = "Review " + meta.name + " COP31 mandate (" + meta.relationship_status + ") and decide outreach sequence.";
    records[iid] = {
      investor_id: iid, stage: defaultStage, owner: owner,
      cop31_venue_or_channel: venue, target_date: targetDate,
      next_action: nextAction, notes: "",
      submitted_docs_count: 0, last_updated_utc: now,
    };
  }
  crmStore = { version: "1.0", stages: PIPELINE_STAGES, updated_at_utc: now, total_entities: Object.keys(records).length, records: records };
  return crmStore;
}

export async function onRequest(context) {
  if (context.request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  }

  try {
    var body = await context.request.json();
    var iid = body.investor_id;
    if (!iid || !INVESTORS_META[iid]) {
      return jsonBody({ error: "Unknown or missing investor_id." }, 400);
    }
    var data = ensureInit();
    var rec = data.records[iid];
    if (!rec) return jsonBody({ error: "Record not found." }, 404);

    var validStages = new Set(PIPELINE_STAGES);
    if (body.stage !== undefined) {
      if (!validStages.has(body.stage)) return jsonBody({ error: "Invalid stage '" + body.stage + "'." }, 400);
      rec.stage = body.stage;
    }
    if (body.owner !== undefined) rec.owner = String(body.owner).trim();
    if (body.cop31_venue_or_channel !== undefined) rec.cop31_venue_or_channel = String(body.cop31_venue_or_channel).trim();
    if (body.target_date !== undefined) rec.target_date = String(body.target_date).trim();
    if (body.next_action !== undefined) rec.next_action = String(body.next_action).trim();
    if (body.notes !== undefined) rec.notes = String(body.notes).trim();
    rec.last_updated_utc = nowISO();

    data.updated_at_utc = nowISO();

    return jsonBody({ updated: true, record: rec, stage_counts: data.stage_counts }, 200);
  } catch (e) {
    return jsonBody({ error: e.message || "Invalid request." }, 400);
  }
}
