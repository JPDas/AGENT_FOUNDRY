resource "aws_bedrock_guardrail" "ai_safety" {
    name                        = "ai-safety-guardrail"
    description                 = "Guardrail to ensure AI safety by preventing harmful content generation"
    blocked_input_messaging    = var.blocked_input_message
    blocked_outputs_messaging   = var.blocked_output_message

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Layer 1: Content Filters
    # Block harmful content across 6 categories
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    content_policy_config {
        # Hate speech
        filters_config {
            type            = "HATE"
            input_strength  = var.content_filter_strengths["hate"]
            output_strength = var.content_filter_strengths["hate"]
        }

        # Insults
        filters_config {
            type            = "INSULTS"
            input_strength  = var.content_filter_strengths["insults"]
            output_strength = var.content_filter_strengths["insults"]
        }

        # Sexual content
        filters_config {
            type            = "SEXUAL"
            input_strength  = var.content_filter_strengths["sexual"]
            output_strength = var.content_filter_strengths["sexual"]
        }

        # Violence
        filters_config {
            type            = "VIOLENCE"
            input_strength  = var.content_filter_strengths["violence"]
            output_strength = var.content_filter_strengths["violence"]
        }

        # Misconduct (illegal activities, etc.)
        filters_config {
            type            = "MISCONDUCT"
            input_strength  = var.content_filter_strengths["misconduct"]
            output_strength = var.content_filter_strengths["misconduct"]
        }

        # Prompt attacks (jailbreaks, prompt injection)
        filters_config {
            type            = "PROMPT_ATTACK"
            input_strength  = "HIGH"    # Always HIGH - no reason to be lenient
            output_strength = "NONE"    # Only applies to input
        }
    }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Layer 2: Denied Topics
    # Block specific topics your AI should never discuss
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    topic_policy_config {
        dynamic "topics_config" {
            for_each = var.denied_topics
            content {
                name       = topics_config.value.name
                definition = topics_config.value.definition
                examples   = topics_config.value.examples
                type       = "DENY"
            }
        }
    }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Layer 3: Word Filters
    # Block profanity + custom words/phrases
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    word_policy_config {
        managed_word_lists_config {
            type = "PROFANITY"
        }

        dynamic "words_config" {
            for_each = var.blocked_words
            content {
                text = words_config.value
            }
        }
    }        
}

# Pin a version for production use
resource "aws_bedrock_guardrail_version" "current" {
  guardrail_arn = aws_bedrock_guardrail.ai_safety.guardrail_arn
  description   = "Guardrail Version managed by Terraform"
}