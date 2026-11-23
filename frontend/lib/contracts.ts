import { z } from "zod";

export const labels = {
  population_size: "Eligible population",
  primary_metric: "Primary metric",
  metric_type: "Outcome type",
  baseline_mean: "Baseline mean",
  baseline_sd: "Baseline standard deviation",
  baseline_conversion_rate: "Baseline conversion rate",
  target_relative_uplift: "Target relative increase",
} as const;
export type FieldName = keyof typeof labels;
const fact = <T extends z.ZodType>(value: T) => z.object({
  value: value.nullable(),
  source: z.enum(["user_provided", "llm_extracted", "missing"]),
  evidence: z.string().nullable(),
  requires_confirmation: z.boolean(),
});
export const extractionResponse = z.object({
  request_id: z.string(),
  status: z.enum(["extraction_complete", "missing_information", "needs_attention"]),
  states: z.array(z.string()),
  facts: z.object({
    population_size: fact(z.number().int()), primary_metric: fact(z.string()),
    metric_type: fact(z.enum(["binary", "continuous"])),
    baseline_mean: fact(z.number()), baseline_sd: fact(z.number()),
    baseline_conversion_rate: fact(z.number()), target_relative_uplift: fact(z.number()),
  }),
  questions: z.array(z.object({
    field: z.enum(Object.keys(labels) as [FieldName, ...FieldName[]]),
    reason: z.enum(["missing", "confirmation"]), question: z.string(),
  })),
  conflicts: z.array(z.object({
    field: z.string(), supplied_value: z.union([z.string(), z.number()]).nullable(),
    extracted_value: z.union([z.string(), z.number()]).nullable(), message: z.string(),
  })),
  metric_wording_note: z.object({
    supplied_value: z.string(), extracted_value: z.string(), message: z.string(),
  }).nullable().default(null),
  statistics_status: z.literal("not_computed"),
  metadata: z.object({
    model: z.string(), prompt_version: z.string(), latency_ms: z.number(),
    attempts: z.number(), input_tokens: z.number().nullable(), output_tokens: z.number().nullable(),
    estimated_cost_usd: z.number().nullable(),
  }),
});
export type ExtractionResponse = z.infer<typeof extractionResponse>;
export type FormValues = { objective: string } & Record<FieldName, string>;

export const designResponse = z.object({
  request_id: z.string(), status: z.enum(["proposal_ready", "needs_attention"]),
  source: z.literal("llm_suggested"), metric_source: z.enum(["user_provided", "llm_suggested"]),
  design: z.object({
    design_family: z.enum(["independent_two_arm", "unsupported", "unclear"]),
    hypothesis: z.string().nullable(), treatment: z.string().nullable(), control: z.string().nullable(),
    randomization_unit: z.string().nullable(), primary_metric: z.string().nullable(),
    observation_period: z.string().nullable(), allocation: z.string().nullable(), rationale: z.string(),
    assumptions: z.array(z.string()), open_questions: z.array(z.string()), limitations: z.array(z.string()),
  }),
  planning_inputs: z.object({
    objective: z.string(), population_size: z.number().nullable(), primary_metric: z.string().nullable(),
    metric_type: z.enum(["binary", "continuous"]).nullable(), baseline_mean: z.number().nullable(),
    baseline_sd: z.number().nullable(), baseline_conversion_rate: z.number().nullable(),
    target_relative_uplift: z.number().nullable(),
  }),
  statistics_status: z.literal("not_computed"), metadata: extractionResponse.shape.metadata,
});
export type DesignResponse = z.infer<typeof designResponse>;

export const emptyForm: FormValues = {
  objective: "", population_size: "", primary_metric: "", metric_type: "",
  baseline_mean: "", baseline_sd: "", baseline_conversion_rate: "", target_relative_uplift: "",
};
export const example = "We want to test personalized credit-card promotions versus generic promotions for 100,000 eligible customers. Our goal is to increase average card spending by 5%.";

export const completeExample: FormValues = {
  objective: `${example}

This is a fully synthetic planning scenario; all values below are fictional assumptions.
Randomly assign independent eligible customers 1:1 to personalized promotions (treatment) or generic promotions (control). Observe each customer for 30 days after assignment.
The primary metric is average card spending, measured in USD per customer during that 30-day window. The baseline mean is 200 USD and the baseline standard deviation is 100 USD for the same metric and window. The minimum meaningful effect is a 5% relative increase over the baseline mean.
For this toy example, assume no overlapping campaigns or spillovers between customers. Keep every assigned customer in the analysis, including zero-spend customers. Plan a fixed-horizon, two-sided comparison with alpha 0.05 and power 0.80; do not stop early based on interim results. No experiment results have been observed.`,
  population_size: "100000",
  primary_metric: "average card spending",
  metric_type: "continuous",
  baseline_mean: "200",
  baseline_sd: "100",
  baseline_conversion_rate: "",
  target_relative_uplift: "0.05",
};

export function toPayload(values: FormValues) {
  return {
    objective: values.objective.trim(),
    ...Object.fromEntries(Object.entries(labels).map(([field]) => {
      const value = values[field as FieldName].trim();
      return [field, value === "" ? null : ["metric_type", "primary_metric"].includes(field)
        ? value : Number(value)];
    })),
  };
}

export const statisticalRequest = z.object({
  design_family: designResponse.shape.design.shape.design_family,
  design_confirmed: z.boolean(), independent_units: z.boolean(),
  primary_metric: z.string().nullable(), metric_type: z.enum(["binary", "continuous"]).nullable(),
  population_size: z.number().int().nullable(), baseline_mean: z.number().nullable(),
  baseline_sd: z.number().nullable(), baseline_conversion_rate: z.number().nullable(),
  effect_type: z.enum(["absolute", "relative"]), effect_value: z.number().nullable(),
  alpha: z.number(), power: z.number(), allocation_ratio: z.number(),
});
export type StatisticalRequest = z.infer<typeof statisticalRequest>;
export const statisticalResult = z.object({
  request_id: z.string(), source: z.literal("derived"),
  status: z.enum(["computed", "insufficient_information", "unsupported_design", "calculation_limit"]),
  inputs: statisticalRequest, n_control: z.number().int().nullable(), n_treatment: z.number().int().nullable(),
  total: z.number().int().nullable(), actual_allocation_ratio: z.number().nullable(),
  achieved_power: z.number().nullable(), absolute_effect: z.number().nullable(), target_rate: z.number().nullable(),
  feasible: z.boolean().nullable(), formula_id: z.string().nullable(), assumptions: z.array(z.string()),
  questions: z.array(z.string()), warnings: z.array(z.string()),
});
export type StatisticalResult = z.infer<typeof statisticalResult>;
export const reviewResponse = z.object({
  request_id: z.string(), status: z.enum(["review_complete", "review_needs_attention"]),
  objective: z.string(), design: designResponse.shape.design, statistics: statisticalResult,
  critique: z.object({
    summary: z.string(), risks: z.array(z.object({
      category: z.string(), severity: z.enum(["high", "medium", "low"]), evidence: z.string(),
      explanation: z.string(), recommendation: z.string(),
    })), unresolved_assumptions: z.array(z.string()),
  }), checks: z.array(z.string()), metadata: extractionResponse.shape.metadata,
});
export type ReviewResponse = z.infer<typeof reviewResponse>;
export type StatisticalForm = Record<"metric_type" | "population_size" | "baseline_mean" | "baseline_sd" |
  "baseline_conversion_rate" | "effect_type" | "effect_value" | "alpha" | "power" | "allocation_ratio", string>;
export function planningForm(design: DesignResponse): StatisticalForm {
  const p = design.planning_inputs;
  return {
    metric_type: p.metric_type ?? "", population_size: p.population_size?.toString() ?? "",
    baseline_mean: p.baseline_mean?.toString() ?? "", baseline_sd: p.baseline_sd?.toString() ?? "",
    baseline_conversion_rate: p.baseline_conversion_rate?.toString() ?? "",
    effect_type: "relative", effect_value: p.target_relative_uplift?.toString() ?? "",
    alpha: "0.05", power: "0.8", allocation_ratio: "1",
  };
}
export function statisticalPayload(form: StatisticalForm, design: DesignResponse, confirmed: boolean): StatisticalRequest {
  const num = (key: keyof StatisticalForm) => form[key].trim() === "" ? null : Number(form[key]);
  return {
    design_family: design.design.design_family, design_confirmed: confirmed, independent_units: confirmed,
    primary_metric: design.design.primary_metric, metric_type: form.metric_type as StatisticalRequest["metric_type"] || null,
    population_size: num("population_size"), baseline_mean: form.metric_type === "binary" ? null : num("baseline_mean"),
    baseline_sd: form.metric_type === "binary" ? null : num("baseline_sd"),
    baseline_conversion_rate: form.metric_type === "continuous" ? null : num("baseline_conversion_rate"),
    effect_type: form.effect_type as "absolute" | "relative", effect_value: num("effect_value"),
    alpha: Number(form.alpha), power: Number(form.power), allocation_ratio: Number(form.allocation_ratio),
  };
}
