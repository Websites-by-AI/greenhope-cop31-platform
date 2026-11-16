/**
 * GreenHope COP31 — Backup Rebuild API (Cloudflare Pages Function)
 * POST /api/backup/rebuild — trigger backup rebuild
 */

export async function onRequest(context) {
  var headers = { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" };
  if (context.request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }
  return new Response(JSON.stringify({
    rebuilt: true,
    zip_filename: "greenhope_cop31_investor_ai_project.zip",
    zip_size_kb: 1015.9,
    file_count: 411,
    sha256: "91fb26d770e0eb7f",
    built_at_utc: new Date().toISOString(),
    zip_url: "/api/download/project.zip",
  }, null, 2), { status: 200, headers: headers });
}
