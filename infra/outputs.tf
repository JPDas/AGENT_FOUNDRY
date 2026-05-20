output "ecr_repository_mcp_uri" {
  value = aws_ecr_repository.mcp-server.repository_url
}

output "ecr_repository_test_agent_uri" {
  value = aws_ecr_repository.test-agent.repository_url
}