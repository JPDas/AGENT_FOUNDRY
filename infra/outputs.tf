output "ecr_repository_mcp_uri" {
  value = aws_ecr_repository.mcp-server.repository_url
}

output "ecr_repository_test_agent_uri" {
  value = aws_ecr_repository.test-agent.repository_url
}

# output "ecr_repository_a2a_agent_uri" {
#   value = aws_ecr_repository.a2a-agent.repository_url
# }

output "guardrail_id" {
  value       = aws_bedrock_guardrail.ai_safety.guardrail_id
  description = "Guardrail ID to pass to Bedrock InvokeModel calls"
}

output "guardrail_version" {
  value       = aws_bedrock_guardrail_version.current.version
  description = "Pinned guardrail version for production use"
}