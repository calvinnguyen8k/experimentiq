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
  statistics_status: z.literal("not_implemented"),
  metadata: z.object({
    model: z.string(), prompt_version: z.string(), latency_ms: z.number(),
    attempts: z.number(), input_tokens: z.number().nullable(), output_tokens: z.number().nullable(),
    estimated_cost_usd: z.number().nullable(),
  }),
});
export type ExtractionResponse = z.infer<typeof extractionResponse>;
export type FormValues = { objective: string } & Record<FieldName, string>;

export const emptyForm: FormValues = {
  objective: "", population_size: "", primary_metric: "", metric_type: "",
  baseline_mean: "", baseline_sd: "", baseline_conversion_rate: "", target_relative_uplift: "",
};
export const example = "We want to test personalized credit-card promotions versus generic promotions for 100,000 eligible customers. Our goal is to increase average card spending by 5%.";

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
