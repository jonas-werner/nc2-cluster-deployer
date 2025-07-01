###################################################################################
#   _  _  ___ ___    ___ _         _                _          _                  
#  | \| |/ __|_  )  / __| |_  _ __| |_ ___ _ _   __| |___ _ __| |___ _  _ ___ _ _ 
#  | .` | (__ / /  | (__| | || (_-<  _/ -_) '_| / _` / -_) '_ \ / _ \ || / -_) '_|
#  |_|\_|\___/___|  \___|_|\_,_/__/\__\___|_|   \__,_\___| .__/_\___/\_, \___|_|  
#                                                        |_|         |__/         
###################################################################################
#  Date:    2025-06-24 (yyyy-mm-dd)
#  Author:  Jonas Werner
#  Web:     https://jonamiki.com 
###################################################################################


import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Config variables from .env
API_VERSION             = os.getenv("API_VERSION")
JSON_WEB_TOKEN          = os.getenv("JSON_WEB_TOKEN")
AWS_REGION              = os.getenv("AWS_REGION")
AWS_AVAILABILITY_ZONE   = os.getenv("AWS_AVAILABILITY_ZONE")
EXISTING_VPC_ID         = os.getenv("EXISTING_VPC_ID")
CLUSTER_SUBNET_ID       = os.getenv("CLUSTER_SUBNET_ID")
PRISM_CENTRAL_SUBNET_ID = os.getenv("PRISM_CENTRAL_SUBNET_ID")
FLOW_SUBNET_ID          = os.getenv("FLOW_SUBNET_ID")
CLUSTER_NAME            = os.getenv("CLUSTER_NAME")
ORGANIZATION_ID         = os.getenv("ORGANIZATION_ID")
AOS_VERSION             = os.getenv("AOS_VERSION")
MANAGEMENT_ACCESS_CIDR  = os.getenv("MANAGEMENT_ACCESS_CIDR")
PRISM_ACCESS_CIDR       = os.getenv("PRISM_ACCESS_CIDR")
HOST_TYPE               = os.getenv("HOST_TYPE")
NUMBER_OF_HOSTS         = int(os.getenv("NUMBER_OF_HOSTS"))
SSH_KEY_NAME            = os.getenv("SSH_KEY_NAME")
NUTANIX_API_BASE_URL    = os.getenv("NUTANIX_API_BASE_URL")

# Fetch and select cloud account
def fetch_and_select_cloud_account(token: str, org_id: str) -> str:

    url = f"{NUTANIX_API_BASE_URL}/api/v2/organizations/{org_id}/cloud-accounts"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch cloud accounts. Status code: {response.status_code}")

            error_data = json.loads(response.text)
            error = error_data["errors"][0]
            for i in error:
                print("%s: %s" % (i, error[i]))

            exit(1)

        data = response.json().get("data", [])
        if not data:
            print("No cloud accounts found for this organization.")
            exit(1)
        print("\nAvailable Cloud Accounts:")
        for idx, acct in enumerate(data, 1):
            print(f"  {idx}. {acct['name']} (provider: {acct['cloud_provider']}, status: {acct['status']})")
        while True:
            try:
                selection = int(input(f"\nSelect the cloud account to use (1-{len(data)}): "))
                if 1 <= selection <= len(data):
                    return data[selection-1]["id"]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    except Exception as e:
        print(f"Error fetching cloud accounts: {e}")
        exit(1)

def build_payload(cloud_account_id: str) -> dict:
    return {
        "data": {
            "advanced_replication": False,
            "aos_version": AOS_VERSION,
            "capacity": [
                {
                    "host_type": HOST_TYPE,
                    "number_of_hosts": NUMBER_OF_HOSTS,
                    "tenancy": "default"
                }
            ],
            "cloud_account_id": cloud_account_id,
            "data_at_rest_encryption": False,
            "host_access_ssh_key": SSH_KEY_NAME,
            "license": "aos",
            "name": CLUSTER_NAME,
            "network": {
                "availability_zone": AWS_AVAILABILITY_ZONE,
                "fvn_config": {
                    "subnet_cloud_id": FLOW_SUBNET_ID
                },
                "fvn_enabled": True,
                "management_services_access_policy": {
                    "ip_addresses": [
                        MANAGEMENT_ACCESS_CIDR
                    ],
                    "mode": "restricted"
                },
                "mode": "existing",
                "prism_element_access_policy": {
                    "ip_addresses": [
                        PRISM_ACCESS_CIDR
                    ],
                    "mode": "restricted"
                },
                "test_network_connectivity": False,
                "vpc": EXISTING_VPC_ID,
                "management_subnet": CLUSTER_SUBNET_ID
            },
            "organization_id": ORGANIZATION_ID,
            "prism_central": {
                "mode": "new",
                "version": "pc.2024.3.1.1",
                "vm_size": "large",
                "management_subnet": PRISM_CENTRAL_SUBNET_ID
            },
            "cluster_fault_tolerance": {
                "factor": "1N/1D"
            },
            "region": AWS_REGION,
            "software_tier": "pro",
            "terminate_at": None,
            "use_case": "general"
        }
    }

def main():
    print("\nNC2 Cluster Creation Script - Existing AWS VPC\n" + "="*50)
    # Fetch and select cloud account
    cloud_account_id = fetch_and_select_cloud_account(JSON_WEB_TOKEN, ORGANIZATION_ID)

    # Build payload
    payload = build_payload(cloud_account_id)

    # Ask if user want to review the payload
    response = input("\nPayload generation complete. Would you like to review the JSON payload? (y/N): ")
    if response.lower() == 'y':
        print("\nCluster creation payload:")
        print(json.dumps(payload, indent=2))

    # Ask for confirmation
    response = input("\nDo you want to proceed with cluster creation? (y/N): ")
    if response.lower() != 'y':
        print("Cluster creation cancelled.")
        exit(0)
    
    url = f"{NUTANIX_API_BASE_URL}/api/v2/clusters/aws"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JSON_WEB_TOKEN}'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    data = response.json().get("data", [])

    if response.status_code in (201, 202):
        print(f"\nStatus code: {response.status_code}")
        print("\nCluster creation request submitted successfully!")
        clusterId = data["cluster_id"]
        print("Cluster ID is: %s\n" % clusterId)
        print("Note: Cluster creation may take 45-60 minutes to complete when FVN is enabled.")
        print("Progress can be monitored through the Nutanix console.\n\n")
    else:
        print("\nCluster creation failed. Please refer to any error messages below.\n")
        error_data = json.loads(response.text)
        error = error_data["errors"][0]
        
        for i in error:
            print("%s: %s" % (i, error[i]))

        print("\nRaw output: %s\n" % error_data)
        exit(1)

if __name__ == "__main__":
    main()
