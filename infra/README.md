# Terraform ECR and IAM Project

This project sets up an Amazon Elastic Container Registry (ECR) and an IAM role using Terraform. It includes all necessary configurations to create the ECR repository, define the IAM role with appropriate permissions, and automate the process of pushing Docker images to the ECR repository.

## Project Structure

```
terraform-ecr-iam
├── ecr.tf                # Configuration for ECR repository
├── iam.tf                # IAM role definition
├── main.tf               # Main entry point for Terraform configuration
├── providers.tf          # Provider configurations
├── variables.tf          # Input variables for the configuration
├── outputs.tf            # Outputs of the Terraform configuration
├── terraform.tfvars.example # Example variable values
├── scripts
│   └── push_to_ecr.sh    # Script to push Docker images to ECR
└── README.md             # Project documentation
```

## Prerequisites

- Terraform installed on your machine.
- AWS CLI configured with appropriate permissions to create ECR and IAM resources.

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd terraform-ecr-iam
   ```

2. **Configure your variables**:
   Copy `terraform.tfvars.example` to `terraform.tfvars` and update the values as needed.

3. **Initialize Terraform**:
   Run the following command to initialize the Terraform configuration:
   ```
   terraform init
   ```

4. **Plan the deployment**:
   Generate an execution plan to see what resources will be created:
   ```
   terraform plan
   ```

5. **Apply the configuration**:
   Deploy the resources defined in the Terraform configuration:
   ```
   terraform apply
   ```

## Pushing Docker Images to ECR

To push a Docker image to the ECR repository, use the provided script:

1. **Make the script executable**:
   ```
   chmod +x scripts/push_to_ecr.sh
   ```

2. **Run the script**:
   ```
   ./scripts/push_to_ecr.sh
   ```

This script will log you into ECR, build your Docker image, tag it appropriately, and push it to the ECR repository.

## Outputs

After running `terraform apply`, you will receive outputs such as the ECR repository URI and IAM role ARN, which can be used for further configurations or integrations.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.