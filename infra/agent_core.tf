# Data sources
data "aws_caller_identity" "current" {}

# ============================================================================
# Agent Execution Role - For AgentCore Runtime
# ============================================================================

resource "aws_iam_role" "agent_execution" {
  name = "my-agent-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AssumeRolePolicy"
      Effect = "Allow"
      Principal = {
        Service = "bedrock-agentcore.amazonaws.com"
      }
      Action = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.id
        }
        ArnLike = {
          "aws:SourceArn" = "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.id}:*"
        }
      }
    }]
  })
}

# Attach AWS managed policy for AgentCore
resource "aws_iam_role_policy_attachment" "agent_execution_managed" {
  role       = aws_iam_role.agent_execution.name
  policy_arn = "arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess"
}

# Inline policy for agent execution
resource "aws_iam_role_policy" "agent_execution" {
  name = "AgentCoreExecutionPolicy"
  role = aws_iam_role.agent_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR Access
      {
        Sid    = "ECRImageAccess"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability"
        ]
        Resource = [
          aws_ecr_repository.test-agent.arn,
          aws_ecr_repository.mcp-server.arn
        ]
      },
      {
        Sid      = "ECRTokenAccess"
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      # CloudWatch Logs
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:DescribeLogStreams",
          "logs:CreateLogGroup",
          "logs:DescribeLogGroups",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.id}:log-group:/aws/bedrock-agentcore/runtimes/*"
      },
     
      # CloudWatch Metrics
      {
        Sid      = "CloudWatchMetrics"
        Effect   = "Allow"
        Action   = ["cloudwatch:PutMetricData"]
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "bedrock-agentcore"
          }
        }
      },
      # Bedrock Model Invocation
      {
        Sid    = "BedrockModelInvocation"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      },
      # Workload Access Tokens
      {
        Sid    = "GetAgentAccessToken"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:GetWorkloadAccessToken",
          "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
          "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.id}:workload-identity-directory/default",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.id}:workload-identity-directory/default/workload-identity/*"
        ]
      }
    ]
  })
}


resource "aws_bedrockagentcore_agent_runtime" "test-agent" {
    agent_runtime_name = "test_agent"
    role_arn = aws_iam_role.agent_execution.arn
    description = "Runtime for test agent"
    
    agent_runtime_artifact {
        container_configuration {
            container_uri = "${aws_ecr_repository.test-agent.repository_url}:latest"
        }
    }

  network_configuration {
    network_mode = "PUBLIC"
  }
  
}

resource "aws_bedrockagentcore_agent_runtime" "mcp-server" {
    agent_runtime_name = "mcp_server"
    role_arn = aws_iam_role.agent_execution.arn
    description = "Runtime for MCP server"
    
    agent_runtime_artifact {
        container_configuration {
            container_uri = "${aws_ecr_repository.mcp-server.repository_url}:latest"
        }
    }

  network_configuration {
    network_mode = "PUBLIC"
  }
  protocol_configuration {
    server_protocol = "MCP"
  }  
}