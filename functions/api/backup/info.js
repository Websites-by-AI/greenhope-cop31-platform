/**
 * GreenHope COP31 — Backup Info API (Cloudflare Pages Function)
 * GET /api/backup/info — backup metadata
 */

export async function onRequest(context) {
  var headers = { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" };
  return new Response(JSON.stringify({
    zip_filename: "greenhope_cop31_investor_ai_project.zip",
    zip_size_kb: 1015.9,
    file_count: 411,
    sha256: "91fb26d770e0eb7f",
    built_at_utc: new Date().toISOString(),
    zip_url: "/api/download/project.zip",
    crm_csv_url: "/api/download/crm?format=csv",
    crm_json_url: "/api/download/crm?format=json",
  }, null, 2), { status: 200, headers: headers });
}
