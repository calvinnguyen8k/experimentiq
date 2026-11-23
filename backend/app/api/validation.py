"""Static, actionable validation feedback without echoing input or exception text."""

CROSS_FIELD_ERRORS = {
    "binary_with_mean": (
        "You selected Binary. Clear baseline mean and standard deviation, or select "
        "Continuous if you are measuring an average such as spending.",
        ["metric_type", "baseline_mean", "baseline_sd"],
    ),
    "continuous_with_rate": (
        "You selected Continuous. Clear baseline conversion rate. "
        "Use baseline mean and standard deviation, or leave them blank if unknown.",
        ["metric_type", "baseline_conversion_rate"],
    ),
    "target_rate_out_of_range": (
        "Baseline conversion rate and target relative increase imply a target of 100% or more. "
        "Reduce the increase or correct the baseline. Enter 0.05 for a 5% increase.",
        ["baseline_conversion_rate", "target_relative_uplift"],
    ),
    "relative_nonpositive_mean": (
        "A relative increase requires a baseline mean greater than zero. "
        "Correct the mean or leave it blank if unknown.",
        ["baseline_mean", "target_relative_uplift"],
    ),
}
FIELD_MESSAGES = {
    "objective": "Describe the experiment in 20–4,000 characters.",
    "population_size": "Eligible population must be a whole number from 2 to 1,000,000,000.",
    "primary_metric": "Primary metric must contain 1–200 characters, or be left blank.",
    "metric_type": "Choose Continuous, Binary, or Not yet known as the outcome type.",
    "baseline_mean": "Baseline mean must be a finite number between -1e12 and 1e12.",
    "baseline_sd": "Baseline standard deviation must be greater than zero and at most 1e12. "
    "Leave it blank if unknown.",
    "baseline_conversion_rate": "Baseline conversion rate must be between 0 and 1, excluding "
    "both endpoints. Enter 0.10 for 10%, or leave it blank if unknown.",
    "target_relative_uplift": "Target relative increase must be greater than 0 and at most 10. "
    "Enter 0.05 for a 5% increase, or leave it blank if unknown.",
}


def validation_feedback(errors: list[dict]) -> tuple[str, list[str]]:
    messages = []
    fields = set()
    for error in errors:
        if error["type"] in CROSS_FIELD_ERRORS:
            message, affected = CROSS_FIELD_ERRORS[error["type"]]
            fields.update(affected)
        else:
            field = next(
                (part for part in error["loc"] if isinstance(part, str) and part in FIELD_MESSAGES),
                None,
            )
            if field:
                fields.add(field)
                message = FIELD_MESSAGES[field]
            elif error["type"] == "json_invalid":
                message = "The request is not valid JSON. Please reload the form and try again."
            else:
                message = "The request contains unsupported fields or has an invalid format."
        if message not in messages:
            messages.append(message)
    return " ".join(messages), sorted(fields)
