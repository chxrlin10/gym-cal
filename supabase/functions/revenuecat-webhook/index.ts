import { createClient } from "https://esm.sh/@supabase/supabase-js@2.49.8";
import { UUID, rcRequest, entitlementSnapshot } from "../_shared/revenuecat.ts";
// Deploy with verify_jwt=false. Authorization is checked here.
Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("method", { status: 405 });
  const secret = Deno.env.get("RC_WEBHOOK_SECRET");
  if (!secret || req.headers.get("Authorization") !== "Bearer " + secret)
    return new Response("unauthorized", { status: 401 });
  try {
    const raw = await req.text();
    if (raw.length > 262144) return new Response("too large", { status: 413 });
    const ev = JSON.parse(raw).event;
    if (!ev || typeof ev.id !== "string" || typeof ev.type !== "string") return new Response("invalid", { status: 400 });
    if (ev.type === "TEST") return new Response("ok");
    const app = Deno.env.get("RC_APP_ID"), environment = Deno.env.get("RC_ENVIRONMENT") || "PRODUCTION";
    if (!app || !["PRODUCTION", "SANDBOX"].includes(environment)) throw new Error("Invalid server configuration");
    if (ev.app_id !== app || (ev.environment && ev.environment !== environment)) return new Response("ignored");
    const transfer = ev.type === "TRANSFER";
    const ids = [...new Set((transfer ? [...(ev.transferred_from || []), ...(ev.transferred_to || [])]
      : [ev.app_user_id, ...(ev.aliases || [])]).filter((x: unknown) => typeof x === "string" && UUID.test(x as string)))];
    if (ids.length > 50) return new Response("invalid", { status: 400 });
    const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    for (const id of ids) {
      const uid = id as string;
      const user = await admin.auth.admin.getUserById(uid);
      if (user.error) { if (user.error.status === 404) continue; throw user.error; }
      if (!user.data.user) continue;
      const pending = await admin.from("account_deletions").select("user_id").eq("user_id", uid).maybeSingle();
      if (pending.error) throw pending.error;
      if (pending.data) continue;
      // Re-read current state instead of interpreting potentially delayed events.
      const r = await rcRequest(uid);
      if (!r.ok) throw new Error("RevenueCat unavailable");
      const snapshot = entitlementSnapshot(await r.json(), environment === "SANDBOX");
      const result = await admin.rpc("apply_rc_snapshot", { p_user_id: uid, p_active: snapshot.active,
        p_product: snapshot.product, p_expires_at: snapshot.expires_at, p_checked_at: snapshot.checked_at });
      if (result.error) throw result.error;
    }
    return new Response("ok");
  } catch (_) { return new Response("retry", { status: 503 }); }
});
