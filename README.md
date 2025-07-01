# NC2 Cluster Creation Script - Existing AWS VPC

This Python script creates an NC2 (Nutanix Cloud Clusters) cluster with Flow enabled in a pre-existing AWS VPC.

## Features

- Creates NC2 cluster in an existing AWS VPC
- Deploys Prism Central
- Enables Flow Virtual Network (FVN)
- Configurable variables for easy maintenance

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Nutanix API access** with appropriate permissions
3. **Existing AWS VPC** with subnets configured. Terraform scripts provided separately for creating these if required
4. **AWS Cloud Account** registered in the NC2 portal
5. **Organization ID** from your Nutanix account in the NC2 portal


## Configuration

Before running the script, you need to update the configuration variables used by the script at runtime: 

### Required Variables
Please create a ".env" file to hold the variables. A sample file called "sample-dot-env-file" has been provided. Remember to change the name to ".env" including the initial "." after updating it. Example of how to fill in the environment file: 
```bash
# Nutanix API Configuration
# Get your JSON Web Token with an API call or from 
# the user Profile -> Advanced page of the NC2 portal
NUTANIX_API_BASE_URL    =https://cloud.nutanix.com
API_VERSION             =v2
JSON_WEB_TOKEN          =your-web-token-here

# AWS Account and Region Configuration
AWS_REGION              =ap-northeast-3
AWS_AVAILABILITY_ZONE   =ap-northeast-3a

# Existing AWS VPC Configuration
EXISTING_VPC_ID         =vpc-aaabbbcccddd

# Subnet Mapping
CLUSTER_SUBNET_ID       =subnet-aaaaaaaaaaaa
PRISM_CENTRAL_SUBNET_ID =subnet-bbbbbbbbbbbb
FLOW_SUBNET_ID          =subnet-cccccccccccc

# Cluster Configuration
CLUSTER_NAME            =awesome-cluster-name
ORGANIZATION_ID         =your-org-id-from-the-nc2-portal

# Make sure the AOS and Prism Central versions are compatible.
# You can find the compatible versions in the Nutanix documentation.
# Example: AOS_VERSION           =7.0.1.5
# Example: PRISM_CENTRAL_VERSION =pc.2024.3.1.1
AOS_VERSION             =7.3
PRISM_CENTRAL_VERSION   =pc.7.3

# Network Access Configuration
# These entries determine the AWS Security group settings, controlling access to the cluster
MANAGEMENT_ACCESS_CIDR  =10.0.0.0/8
PRISM_ACCESS_CIDR       =10.0.0.0/8

# Host Configuration
# Single host clusters are supported for non-prod use but cannot be scaled up. 
# Use a 3 node or larger cluster for production 
HOST_TYPE               =i3.metal
NUMBER_OF_HOSTS         =1

# SSH Key Configuration
# Your EC2 key pair name
SSH_KEY_NAME            =your-key-name
```


## Usage

1. **Clone or download this repository**
```bash
git clone https://github.com/jonas-werner/nc2-cluster-deployer.git
```
2. **Create and activate a Python virtual environment**: 
```bash
python3 -m venv <virtual-env-name>
source ./<virtual-env-name>/bin/activate
```
3. Install the required dependencies with pip:
```bash
pip install -r requirements.txt
```
4. **Update Configuration**: Modify the variables in the .env file and save in the same directory as the script
5. **Run the Script**: Execute the script from the command line:

```bash
python ./create_nc2_cluster_in_existing_aws_vpc.py
```

6. **Review and Confirm**: The script will:
   - Validate your configuration
   - Ask which cloud account to use
   - Display the cluster creation payload (optionally)
   - Ask for confirmation before proceeding
   - Submit the cluster creation request
   - Let you know if it succeeds or if it crashes and burns

### Example
Example of running the script from the command line. 
```bash
python ./create_nc2_cluster_in_existing_aws_vpc.py

NC2 Cluster Creation Script - Existing AWS VPC
==================================================

Available Cloud Accounts:
  1. My AWS Account (provider: aws, status: ready)
  2. My Azure Account (provider: azure, status: ready)

Select the cloud account to use (1-2): 1

Payload generation complete. Would you like to review the JSON payload? (y/N):

Do you want to proceed with cluster creation? (y/N): y

Status code: 202

Cluster creation request submitted successfully!
Cluster ID is: aaaabbbbee-1122-3344-5566-aabbccddeeffgg

Note: Cluster creation may take 45-60 minutes to complete when FVN is enabled.
Progress can be viewed through the Nutanix console.
```

### Subnet Mapping

NC2 clusters require three distinct subnets for different components:

- **Management Subnet** (`management_subnet_id`): Used for the bare-metal cluster hosts (data plane)
- **Prism Central Subnet** (`prism_central.subnet.subnet_cloud_id`): Used for Prism Central management services  
- **Flow Subnet** (`fvn_config.subnet_cloud_id`): Used for Flow Virtual Network (FVN) functionality

Each subnet serves a specific purpose and must be properly configured in your existing VPC. The subnets are referenced in various sections in the REST payload and deployment will fail if they are not accurate. 

## Example Payload Structure 
The payload will optionally be displayed prior to cluster creation during script execution. 

```json
{
  "data": {
    "name": "My-NC2-Cluster",
    "network": {
      "mode": "existing",
      "vpc_id": "vpc-12345678",
      "management_subnet_id": "subnet-12345678",
      "fvn_enabled": true,
      "fvn_config": {
        "subnet_cloud_id": "subnet-11223344"
      }
    },
    "prism_central": {
      "id": "existing",
      "mode": "existing",
      "subnet": {
        "subnet_cloud_id": "subnet-87654321"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Authentication Issues**: Ensure your JWT is valid. It expires frequently
2. **VPC/Subnet Issues**: Verify that the VPC and subnet IDs exist and are accessible
3. **Region Mismatch**: Ensure the AWS region and AZ matches your VPC and subnet configuration
4. **Network Connectivity**: Check that your VPC has proper internet connectivity


## More info

- **Nutanix API**: Refer to the [Nutanix Developer Portal](https://www.nutanix.dev)
- **NC2 Documentation**: Check the [Nutanix v4 API documentation](https://developers.nutanix.com)
- **Other scripts and info**: [https://jonamiki.com](https://jonamiki.com)

