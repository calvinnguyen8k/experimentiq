import { designResponse, extractionResponse, FormValues, toPayload, statisticalResult, StatisticalRequest, reviewResponse, DesignResponse } from "./contracts";

export class ApiError extends Error {
  constructor(message: string, public requestId?: string, public fields: string[] = []) {
    super(message);
  }
}

async function post(path: string, body: unknown, signal: AbortSignal) {
  const url = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const response = await fetch(`${url}/api/v1/${path}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body), signal, cache: "no-store",
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
  return data;
}

export async function extractExperiment(form: FormValues, signal: AbortSignal) {
  const parsed = extractionResponse.safeParse(await post("experiments/extract", toPayload(form), signal));
  if (!parsed.success) throw new ApiError("The response did not match the expected format. Please try again.");
  return parsed.data;
}

export async function generateDesign(form: FormValues, signal: AbortSignal) {
  const parsed = designResponse.safeParse(await post("experiments/design", toPayload(form), signal));
  if (!parsed.success) throw new ApiError("The design response did not match the expected format. Please try again.");
  return parsed.data;
}

export async function calculateStatistics(inputs: StatisticalRequest, signal: AbortSignal) {
  const parsed = statisticalResult.safeParse(await post("statistics/sample-size", inputs, signal));
  if (!parsed.success) throw new ApiError("The calculation response has an invalid format. Please retry.");
  return parsed.data;
}
export async function reviewExperiment(design: DesignResponse, inputs: StatisticalRequest, signal: AbortSignal) {
  const parsed = reviewResponse.safeParse(await post("experiments/review", {
    objective: design.planning_inputs.objective, design: design.design, statistical_request: inputs,
  }, signal));
  if (!parsed.success) throw new ApiError("The review response has an invalid format. Please retry.");
  return parsed.data;
}
