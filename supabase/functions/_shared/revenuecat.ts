// Server-only: never copy RC_SECRET_KEY to HTML or a public repository.
export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export async function rcRequest(uid: string, method = "GET") {
  const key = Deno.env.get("RC_SECRET_KEY");
  if (!key) throw new Error("RevenueCat server key not configured");
  return await fetch("https://api.revenuecat.com/v1/subscribers/" + encodeURIComponent(uid), {
    method, headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" },
    signal: AbortSignal.timeout(12000),
  });
}
export function entitlementSnapshot(body: any, sandbox: boolean) {
  const sub = body.subscriber;
  if (!sub || !Number.isFinite(body.request_date_ms)) throw new Error("Invalid RevenueCat response");
  const ent = sub.entitlements?.premium;
  const product = ent?.product_identifier ?? null;
  const purchase = product ? sub.subscriptions?.[product] : null;
  const expiration = Date.parse(ent?.expires_date || "");
  const grace = Date.parse(ent?.grace_period_expires_date || purchase?.grace_period_expires_date || "");
  const until = Math.max(Number.isFinite(expiration) ? expiration : 0, Number.isFinite(grace) ? grace : 0);
  // This app sells recurring Google Play subscriptions, not lifetime entitlements.
  const valid = !!ent && !!purchase && purchase.store === "play_store" &&
    purchase.is_sandbox === sandbox && !purchase.refunded_at && until > body.request_date_ms;
  return { active: valid, product, expires_at: until ? new Date(until).toISOString() : null,
    checked_at: new Date(body.request_date_ms).toISOString() };
}
