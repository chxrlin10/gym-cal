import { createClient } from "https://esm.sh/@supabase/supabase-js@2.49.8";
import { rcRequest } from "../_shared/revenuecat.ts";
const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "authorization, apikey, content-type", "Access-Control-Allow-Methods": "POST, OPTIONS" };
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return new Response("method", { status: 405, headers: cors });
  // Configuração conferida ANTES de marcar a exclusão. Antes, sem RC_SECRET_KEY nem RC_ENABLED=false, a função
  // gravava a pendência e só depois falhava: o usuário ficava bloqueado para novos envios sem a conta ser apagada.
  const rcKey = Deno.env.get("RC_SECRET_KEY"), billingOff = Deno.env.get("RC_ENABLED") === "false";
  if (!Deno.env.get("SUPABASE_URL") || !Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || (!rcKey && !billingOff))
    return new Response("Deletion unavailable: server not configured; nothing was changed", { status: 503, headers: cors });
  try {
    const token = (req.headers.get("Authorization") || "").replace(/^Bearer /, "");
    const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const { data, error } = await admin.auth.getUser(token);
    if (error || !data.user) return new Response("unauthorized", { status: 401, headers: cors });
    const uid = data.user.id;
    // Mark first: failed/retried requests cannot re-upload or re-grant Premium.
    const mark = await admin.from("account_deletions").upsert({ user_id: uid });
    if (mark.error) throw mark.error;
    if (rcKey) {
      const rc = await rcRequest(uid, "DELETE");
      if (!rc.ok && rc.status !== 404) throw new Error("Provider deletion pending");
    }
    // Requires the CASCADE FKs supplied in migration.sql. No prior user_data DELETE.
    const del = await admin.auth.admin.deleteUser(uid);
    if (del.error) throw del.error;
    return new Response("ok", { headers: cors });
  } catch (_) { return new Response("Deletion pending; retry or contact support", { status: 503, headers: cors }); }
});
