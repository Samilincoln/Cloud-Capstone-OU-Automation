# organizational_unit.py
from typing import Optional
from botocore.exceptions import ClientError
from aws_auto.aws_client import get_client
from aws_auto.log_handler import log_info, log_error

def list_root_id(org_client=None) -> str:
    org_client = org_client or get_client("organizations")
    resp = org_client.list_roots()
    return resp["Roots"][0]["Id"]

def resolve_ou_id(org_client, *, ou_name: Optional[str] = None, ou_id: Optional[str] = None) -> str:
    """
    Return OU ID resolved from name or return provided ou_id directly.
    Raises ValueError if not found.
    """
    if ou_id:
        return ou_id

    if not ou_name:
        raise ValueError("Either ou_name or ou_id must be provided")

    root_id = list_root_id(org_client)
    paginator = org_client.get_paginator("list_organizational_units_for_parent")
    for page in paginator.paginate(ParentId=root_id):
        for ou in page.get("OrganizationalUnits", []):
            if ou.get("Name") == ou_name:
                log_info(f"Resolved OU name '{ou_name}' to ID {ou['Id']}")
                return ou["Id"]

    raise ValueError(f"OU with name '{ou_name}' not found under root {root_id}")

# CREATE
def create_organizational_unit(ou_name: str, org_client=None):
    """
    Create an OU under the root. If exists, reuse the existing OU ID.
    Returns dict with OUName and OUID.
    """
    org_client = org_client or get_client("organizations")
    parent_id = list_root_id(org_client)

    # Try to create
    try:
        resp = org_client.create_organizational_unit(ParentId=parent_id, Name=ou_name)
        ou = resp["OrganizationalUnit"]
        log_info(f"Created OU '{ou_name}' with ID {ou['Id']}")
        return {"OUName": ou_name, "OUID": ou["Id"]}
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "DuplicateOrganizationalUnitException":
            # find and reuse
            try:
                ou_id = resolve_ou_id(org_client, ou_name=ou_name)
                log_info(f"OU '{ou_name}' already exists (ID {ou_id}), reusing.")
                return {"OUName": ou_name, "OUID": ou_id}
            except ValueError:
                log_error(f"Duplicate error but OU not resolvable: {exc}")
                raise
        else:
            log_error(f"Failed to create OU {ou_name}: {exc}")
            raise


# LIST
def list_organizational_units(org_client=None) -> List[Dict[str, str]]:
    org_client = org_client or get_client("organizations")
    root_id = list_root_id(org_client)
    paginator = org_client.get_paginator("list_organizational_units_for_parent")
    ous = []
    for page in paginator.paginate(ParentId=root_id):
        ous.extend(page.get("OrganizationalUnits", []))
    log_info(f"Retrieved {len(ous)} OUs under root {root_id}")
    return ous


# UPDATE (Rename OU)
def update_organizational_unit(ou_id: str, new_name: str, org_client=None) -> Dict[str, str]:
    org_client = org_client or get_client("organizations")
    try:
        resp = org_client.update_organizational_unit(OrganizationalUnitId=ou_id, Name=new_name)
        ou = resp["OrganizationalUnit"]
        log_info(f"Renamed OU ID {ou_id} to '{new_name}'")
        return {"OUName": new_name, "OUID": ou["Id"]}
    except ClientError as exc:
        log_error(f"Failed to update OU {ou_id}: {exc}")
        raise


# DELETE
def delete_organizational_unit(ou_id: str, org_client=None) -> bool:
    org_client = org_client or get_client("organizations")
    try:
        org_client.delete_organizational_unit(OrganizationalUnitId=ou_id)
        log_info(f"Deleted OU ID {ou_id}")
        return True
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "OrganizationalUnitNotEmptyException":
            log_error(f"OU {ou_id} not empty — remove child accounts first.")
        else:
            log_error(f"Failed to delete OU {ou_id}: {exc}")
        return False