output "ecr_repository_uri" {
  value = aws_ecr_repository.myapp.repository_url
}

output "bedrock_memory_id" {
  value = aws_bedrockagentcore_memory.my_agent_memory.id
}
