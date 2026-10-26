import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const bucket = "camera-captures";
const maxUploadBytes = 5 * 1024 * 1024;
const maxUploadsPerHour = 5;
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Vary": "Origin",
};

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json; charset=utf-8" },
  });
}

function readKeyDictionary(environmentName: string): Record<string, string> {
  const value = Deno.env.get(environmentName);
  if (!value) return {};
  const parsed: unknown = JSON.parse(value);
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error(`${environmentName} must contain a JSON object`);
  }
  return Object.fromEntries(
    Object.entries(parsed).filter((entry): entry is [string, string] =>
      typeof entry[1] === "string"
    ),
  );
}

function getFirstKey(keys: Record<string, string>): string | undefined {
  return keys.default ?? Object.values(keys)[0];
}

function getClient(supabaseUrl: string, serviceRoleKey: string) {
  return createClient(supabaseUrl, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

async function hashClientAddress(request: Request): Promise<string> {
  const address = request.headers.get("cf-connecting-ip") ??
    request.headers.get("x-real-ip") ??
    request.headers.get("x-forwarded-for")?.split(",")[0].trim() ??
    "unknown";
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(address),
  );
  return Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, "0")
  ).join("");
}

async function readBoundedImage(request: Request): Promise<Uint8Array | null> {
  const reader = request.body?.getReader();
  if (!reader) return new Uint8Array();

  const chunks: Uint8Array[] = [];
  let totalBytes = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    totalBytes += value.length;
    if (totalBytes > maxUploadBytes) {
      await reader.cancel();
      return null;
    }
    chunks.push(value);
  }

  const image = new Uint8Array(totalBytes);
  let offset = 0;
  for (const chunk of chunks) {
    image.set(chunk, offset);
    offset += chunk.length;
  }
  return image;
}

Deno.serve(async (request: Request) => {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  let publishableKeys: Record<string, string>;
  let secretKeys: Record<string, string>;
  try {
    publishableKeys = readKeyDictionary("SUPABASE_PUBLISHABLE_KEYS");
    secretKeys = readKeyDictionary("SUPABASE_SECRET_KEYS");
  } catch (error) {
    console.error("Supabase API keys are misconfigured:", error);
    return jsonResponse({ error: "Gallery service is not configured" }, 503);
  }
  const acceptedApiKeys = [
    Deno.env.get("SUPABASE_ANON_KEY"),
    ...Object.values(publishableKeys),
  ].filter((key): key is string => Boolean(key));
  if (!acceptedApiKeys.includes(request.headers.get("apikey") ?? "")) {
    return jsonResponse({ error: "Unauthorized" }, 401);
  }

  if (request.method !== "POST") {
    return jsonResponse({ error: "Method not allowed" }, 405);
  }
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ??
    getFirstKey(secretKeys);
  if (!supabaseUrl || !serviceRoleKey) {
    console.error("Supabase function secrets are not configured");
    return jsonResponse({ error: "Gallery service is not configured" }, 503);
  }
  const supabase = getClient(supabaseUrl, serviceRoleKey);

  if (request.method === "GET") {
    const { data, error } = await supabase.storage.from(bucket).list("", {
      limit: 100,
      sortBy: { column: "created_at", order: "desc" },
    });
    if (error) {
      console.error("Could not list camera captures:", error.message);
      return jsonResponse({ error: "Could not load camera captures" }, 500);
    }
    const images = (data ?? [])
      .filter((file) => /^camera_capture_[\w-]+\.jpg$/.test(file.name))
      .map((file) => ({
        src: supabase.storage.from(bucket).getPublicUrl(file.name).data.publicUrl,
        caption: "Camera capture",
      }));
    return jsonResponse({ images });
  }

  if (request.headers.get("content-type")?.split(";")[0].trim() !== "image/jpeg") {
    return jsonResponse({ error: "Only JPEG camera captures are accepted" }, 415);
  }

  const contentLength = Number(request.headers.get("content-length"));
  if (Number.isFinite(contentLength) && contentLength > maxUploadBytes) {
    return jsonResponse({ error: "Camera capture must be under 5 MB" }, 413);
  }

  const image = await readBoundedImage(request);
  if (!image) {
    return jsonResponse({ error: "Camera capture must be under 5 MB" }, 413);
  }
  if (image.length < 4) {
    return jsonResponse({ error: "Camera capture is empty or incomplete" }, 400);
  }
  if (
    image[0] !== 0xff || image[1] !== 0xd8 || image[2] !== 0xff ||
    image[image.length - 2] !== 0xff || image[image.length - 1] !== 0xd9
  ) {
    return jsonResponse({ error: "Invalid JPEG image" }, 400);
  }

  const windowStart = new Date(Math.floor(Date.now() / 3_600_000) * 3_600_000);
  const { data: allowed, error: rateLimitError } = await supabase.rpc(
    "consume_camera_capture_rate_limit",
    {
      p_ip_hash: await hashClientAddress(request),
      p_window_start: windowStart.toISOString(),
      p_limit: maxUploadsPerHour,
    },
  );
  if (rateLimitError) {
    console.error("Could not check camera capture rate limit:", rateLimitError.message);
    return jsonResponse({ error: "Could not accept camera capture" }, 500);
  }
  if (!allowed) {
    return jsonResponse({ error: "Upload limit reached. Please try again later." }, 429);
  }

  const filename = `camera_capture_${new Date().toISOString().replace(/[:.]/g, "-")}_${crypto.randomUUID()}.jpg`;
  const { error: uploadError } = await supabase.storage.from(bucket).upload(
    filename,
    image,
    { contentType: "image/jpeg", upsert: false },
  );
  if (uploadError) {
    console.error("Could not save camera capture:", uploadError.message);
    return jsonResponse({ error: "Could not save camera capture" }, 500);
  }

     return jsonResponse({ ok: true }, 201);
});
