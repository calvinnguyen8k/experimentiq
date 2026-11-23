import { extractionResponse, FormValues, toPayload } from "./contracts";

export class ApiError extends Error {
  constructor(message: string, public requestId?: string, public fields: string[] = []) {
    super(message);
  }
}

export async function extractExperiment(form: FormValues, signal: AbortSignal) {
  const url = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const response = await fetch(`${url}/api/v1/experiments/extract`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(toPayload(form)), signal, cache: "no-store",
  });
  let data;
  try { data = await response.json(); }
  catch { throw new ApiError("The service returned an unreadable response. Please try again."); }
  if (!response.ok) {
    const error = data?.error;
    throw new ApiError(
      typeof error?.message === "string" ? error.message : "The service could not complete the request.",
      typeof error?.request_id === "string" ? error.request_id : undefined,
      Array.isArray(error?.fields) ? error.fields.filter((f: unknown) => typeof f === "string") : [],
    );
  }
  const parsed = extractionResponse.safeParse(data);
  if (!parsed.success) throw new ApiError("The response did not match the expected format. Please try again.");
  return parsed.data;
}
