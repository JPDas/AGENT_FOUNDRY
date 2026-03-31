output "ecr_repository_uri" {
  value = aws_ecr_repository.myapp.repository_url
}
