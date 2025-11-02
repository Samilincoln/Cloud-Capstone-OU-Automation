# account.py
import time
from typing import Dict, Any
from botocore.exceptions import ClientError
from aws_auto.aws_client import get_client
from aws_auto.organizational_unit import resolve_ou_id, list_root_id
from aws_auto.log_handler import log_info, log_error

POLL_INTERVAL = 20
POLL_TIMEOUT = 60 * 15  # 15 minutes

def create_member_account(account_name: str, account_email: str, ou: str, role_name: str = "OrgAdminRole") -> Dict[str, Any]:
    """
    Create a member account and move it into the specified OU (by name or ID).
    Returns dict with account details.
    """
    org_client = get_client("organizations")

    # Resolve parent OU ID or accept as id
    try:
        parent_ou_id = resolve_ou_id(org_client, ou_name=ou) if not ou.startswith("ou-") else ou
    except Exception:
        # try directly treating as id if startswith ou-
        if ou.startswith("ou-"):
            parent_ou_id = ou
        else:
            raise

    root_id = list_root_id(org_client)
    log_info(f"Using Root ID {root_id}, Target OU ID {parent_ou_id}")

    # Start account creation
    try:
        resp = org_client.create_account(Email=account_email, AccountName=account_name, RoleName=role_name, IamUserAccessToBilling="ALLOW")
        request_id = resp["CreateAccountStatus"]["Id"]
        log_info(f"Account creation started for {account_name}, request id {request_id}")
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "ConcurrentCreationLimitExceededException":
            log_error("Concurrent account creation limit reached. Try again later.")
        else:
            log_error(f"Failed to initiate account creation: {exc}")
        raise

    # Poll status
    start = time.time()
    while True:
        status = org_client.describe_create_account_status(CreateAccountRequestId=request_id)["CreateAccountStatus"]
        state = status["State"]
        if state == "SUCCEEDED":
            account_id = status["AccountId"]
            log_info(f"Account creation succeeded: {account_name} -> {account_id}")
            break
        if state == "FAILED":
            reason = status.get("FailureReason", "Unknown")
            log_error(f"Account creation failed: {reason}")
            raise RuntimeError(f"Account creation failed: {reason}")
        if time.time() - start > POLL_TIMEOUT:
            log_error("Account creation timed out.")
            raise TimeoutError("Account creation timed out")

        log_info("Waiting for account creation to complete...")
        time.sleep(POLL_INTERVAL)

    # Move account to OU
    try:
        org_client.move_account(AccountId=account_id, SourceParentId=root_id, DestinationParentId=parent_ou_id)
        log_info(f"Moved account {account_id} to OU {parent_ou_id}")
    except ClientError as exc:
        log_error(f"Failed to move account {account_id} to OU {parent_ou_id}: {exc}")
        raise

    result = {
        "AccountId": account_id,
        "AccountName": account_name,
        "AccountEmail": account_email,
        "OUID": parent_ou_id,
    }
    return result


# READ
def list_member_accounts(org_client=None) -> List[Dict[str, Any]]:
    org_client = org_client or get_client("organizations")
    paginator = org_client.get_paginator("list_accounts")
    accounts = []
    for page in paginator.paginate():
        accounts.extend(page.get("Accounts", []))
    log_info(f"Retrieved {len(accounts)} member accounts.")
    return accounts


# READ ACCOUNT DETAILS
def get_account_details(account_id: str, org_client=None) -> Dict[str, Any]:
    org_client = org_client or get_client("organizations")
    try:
        resp = org_client.describe_account(AccountId=account_id)
        account = resp["Account"]
        log_info(f"Retrieved account details for {account_id}")
        return account
    except ClientError as exc:
        log_error(f"Failed to get account {account_id}: {exc}")
        raise


# UPDATE (Move Account between OUs)
def move_account_to_ou(account_id: str, destination_ou: str, org_client=None) -> Dict[str, str]:
    org_client = org_client or get_client("organizations")

    try:
        dest_ou_id = resolve_ou_id(org_client, ou_name=destination_ou) if not destination_ou.startswith("ou-") else destination_ou
        current_parent = org_client.list_parents(ChildId=account_id)["Parents"][0]["Id"]
        org_client.move_account(AccountId=account_id, SourceParentId=current_parent, DestinationParentId=dest_ou_id)
        log_info(f"Moved account {account_id} to OU {dest_ou_id}")
        return {"AccountId": account_id, "NewOUID": dest_ou_id}
    except ClientError as exc:
        log_error(f"Failed to move account {account_id}: {exc}")
        raise


# DELETE (Close Account)
def close_member_account(account_id: str, org_client=None) -> bool:
    org_client = org_client or get_client("organizations")
    try:
        org_client.close_account(AccountId=account_id)
        log_info(f"Closed member account {account_id}")
        return True
    except ClientError as exc:
        log_error(f"Failed to close account {account_id}: {exc}")
        return False