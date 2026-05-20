resource "aws_ecr_repository" "test-agent" {
    name                 = "test-agent"
    image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "mcp-server" {
    name                 = "mcp-server"
    image_tag_mutability = "MUTABLE"
}