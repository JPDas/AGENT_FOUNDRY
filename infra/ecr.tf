resource "aws_ecr_repository" "myapp" {
    name                 = "myapp"
    image_tag_mutability = "MUTABLE"
}