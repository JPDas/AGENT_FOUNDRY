data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "memory_role" {
  name               = "bedrock-agentcore-memory-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "memory_role_attachment" {
  role       = aws_iam_role.memory_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockAgentCoreMemoryBedrockModelInferenceExecutionRolePolicy"
}


resource "aws_bedrockagentcore_memory" "my_agent_memory" {
    name                  = "my_agent_memory"
    event_expiry_duration = 30
  
}