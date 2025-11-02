# iam_roles.py
from typing import Dict
import json
import time
from botocore.exceptions import ClientError
from aws_auto.aws_client import get_client
from aws_auto.log_handler import log_info, log_error

# The role trust policy used for the role we create (management account can assume)
TRUST_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},  # tightened below when used
            "Action": "sts:AssumeRole",
        }
    ],
}

ORG_FULL_ACCESS_ARN = "arn:aws:iam::aws:policy/AWSOrganizationsFullAccess"

def create_or_get_role(role_name: str, trust_principal_arn: str = None) -> Dict:
    """
    Create an IAM role if not exists, attach AWSOrganizationsFullAccess, and return role arn.
    trust_principal_arn: if provided, substitutes the Principal to a specific ARN.
    """
    iam = get_client("iam")
    role_arn = None

    trust_policy = TRUST_POLICY.copy()
    if trust_principal_arn:
        trust_policy["Statement"][0]["Principal"] = {"AWS": trust_principal_arn}

    try:
        resp = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role created for aws_auto OU automation",
        )
        role_arn = resp["Role"]["Arn"]
        log_info(f"Created IAM role {role_name} ({role_arn})")
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "EntityAlreadyExists":
            resp = iam.get_role(RoleName=role_name)
            role_arn = resp["Role"]["Arn"]
            log_info(f"Reusing existing IAM role {role_name} ({role_arn})")
        else:
            log_error(f"Failed to create/get role {role_name}: {exc}")
            raise

    # Attach policy (idempotent)
    try:
        iam.attach_role_policy(RoleName=role_name, PolicyArn=ORG_FULL_ACCESS_ARN)
        log_info(f"Attached {ORG_FULL_ACCESS_ARN} to {role_name}")
    except ClientError as exc:
        log_error(f"Failed to attach policy to {role_name}: {exc}")
        raise

    return {"role_name": role_name, "role_arn": role_arn}


def assume_role(role_arn: str, session_name: str = "aws_auto_session", duration_seconds: int = 3600) -> Dict:
    sts = get_client("sts")
    try:
        resp = sts.assume_role(RoleArn=role_arn, RoleSessionName=session_name, DurationSeconds=duration_seconds)
        creds = resp["Credentials"]
        log_info(f"Assumed role {role_arn}. Session expires at {creds['Expiration']}")
        return {
            "AccessKeyId": creds["AccessKeyId"],
            "SecretAccessKey": creds["SecretAccessKey"],
            "SessionToken": creds["SessionToken"],
            "Expiration": creds["Expiration"],
        }
    except Exception as exc:
        log_error(f"Failed to assume role: {exc}")
        raise
