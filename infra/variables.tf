
variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "blocked_input_message" {
  type        = string
  description = "Message shown when user input is blocked"
  default     = "Your message could not be processed. Please rephrase your request without including harmful content, personal information, or off-topic questions."
}

variable "blocked_output_message" {
  type        = string
  description = "Message shown when model output is blocked"
  default     = "The response was filtered for safety. Please try rephrasing your question."
}


# ━━━ Content Filter Strengths ━━━
variable "content_filter_strengths" {
  type        = map(string)
  description = "Filter strength per category: NONE, LOW, MEDIUM, HIGH"
  default = {
    hate       = "HIGH"
    insults    = "HIGH"
    sexual     = "HIGH"
    violence   = "HIGH"
    misconduct = "HIGH"
  }
}

# ━━━ Denied Topics ━━━
variable "denied_topics" {
  type = list(object({
    name       = string
    definition = string
    examples   = list(string)
  }))
  description = "Topics the AI should refuse to discuss"
  default     = [
    {
      name       = "Competitor Comparison"
      definition = "Questions comparing the AI's product to competitors"
      examples   = [
        "How does your product compare to CompetitorCo?",
        "Is CompetitorCo better than you?",
        "What are the alternatives to your service?"
      ]
    }
  ]
}

# ━━━ Blocked Words ━━━
variable "blocked_words" {
  type        = list(string)
  description = "Exact words/phrases to block"
  default     = ["confidential", "internal-only"]
}
