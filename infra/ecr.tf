resource "aws_ecr_repository" "test-agent" {
    name                 = "test-agent"
    image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "mcp-server" {
    name                 = "mcp-server"
    image_tag_mutability = "MUTABLE"
}

# resource "aws_ecr_repository" "a2a-agent" {
#     name                 = "a2a-agent"
#     image_tag_mutability = "MUTABLE"
# }