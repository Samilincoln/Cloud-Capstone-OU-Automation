# organization.py
from botocore.exceptions import ClientError
from aws_auto.aws_client import get_client
from aws_auto.log_handler import log_info, log_error

def get_organization(org_client=None):
    """
    Return organization details, or None if not present.
    """
    org_client = org_client or get_client("organizations")
    try:
        resp = org_client.describe_organization()
        log_info("Organization exists and was retrieved.")
        return resp["Organization"]
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("AWSOrganizationsNotInUseException", "AccessDeniedException", "InvalidInputException"):
            log_error(f"Could not describe organization: {exc}")
            return None
        raise

def create_organization_if_missing(org_client=None):
    org_client = org_client or get_client("organizations")
    try:
        resp = org_client.create_organization(FeatureSet="ALL")
        log_info("Organization created.")
        return resp["Organization"]
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code == "AWSOrganizationsNotInUseException":
            # Should not happen; treat as error
            log_error("AWS Organizations not in use.")
            raise
        if code == "AlreadyInOrganizationException":
            log_info("Already in an organization; returning current organization.")
            return get_organization(org_client=org_client)
        if code == "AccessDeniedException":
            log_error("Access denied when creating organization. Are you running as root/management account?")
            raise
        raise


def update_organization_tags(tags: dict, org_client=None):
    """
    Simulate an 'update' by applying tags to the organization.
    AWS Organizations only supports tagging or changing FeatureSets.
    """
    org_client = org_client or get_client("organizations")
    org = get_organization(org_client)
    if not org:
        log_error("No organization found to update.")
        return None

    try:
        org_client.tag_resource(
            ResourceId=org["Id"],
            Tags=[{"Key": k, "Value": v} for k, v in tags.items()],
        )
        log_info(f"Organization tags updated: {tags}")
        return {"OrganizationId": org["Id"], "Tags": tags}
    except ClientError as exc:
        log_error(f"Failed to tag organization: {exc}")
        raise


def delete_organization(org_client=None):
    """
    Delete the AWS Organization. Must be run by the management account.
    """
    org_client = org_client or get_client("organizations")
    try:
        org_client.delete_organization()
        log_info("Organization deleted successfully.")
        return True
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code == "AWSOrganizationsNotInUseException":
            log_error("No organization exists to delete.")
            return False
        if code == "AccessDeniedException":
            log_error("Access denied: only root/management account can delete an organization.")
            raise
        log_error(f"Failed to delete organization: {exc}")
        raise