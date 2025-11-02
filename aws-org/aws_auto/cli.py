# cli.py
import click
from aws_auto.organizational_unit import (
    create_organizational_unit,
    resolve_ou_id,
    list_root_id
)
from aws_auto.account import (
    create_member_account,
    list_member_accounts,
    get_account_details,
    move_account_to_ou,
    close_member_account
)
from aws_auto.log_handler import log_info, log_error


@click.group()
def cli():
    """aws_auto — AWS OU & Account Automation CLI"""
    pass


# ========== ORGANIZATIONAL UNIT COMMANDS ==========

@cli.command("create-ou")
@click.argument("ou_name")
def create_ou_cmd(ou_name):
    """Create or reuse an Organizational Unit (OU)"""
    try:
        res = create_organizational_unit(ou_name)
        click.echo(f"OU created or reused: {res}")
        log_info(f"OU created or reused: {res}")
    except Exception as exc:
        log_error(f"Failed to create OU: {exc}")
        raise click.Abort()


@cli.command("get-ou")
@click.argument("ou_name")
def get_ou_cmd(ou_name):
    """Retrieve OU ID by name"""
    try:
        ou_id = resolve_ou_id(None, ou_name=ou_name)
        click.echo(f"OU '{ou_name}' found with ID: {ou_id}")
        log_info(f"Retrieved OU ID {ou_id} for {ou_name}")
    except Exception as exc:
        log_error(f"Failed to get OU: {exc}")
        raise click.Abort()


@cli.command("list-root")
def list_root_cmd():
    """List root organizational unit ID"""
    try:
        root_id = list_root_id()
        click.echo(f"Root ID: {root_id}")
    except Exception as exc:
        log_error(f"Failed to list root: {exc}")
        raise click.Abort()


# ========== ACCOUNT COMMANDS ==========

@cli.command("create-account")
@click.argument("account_name")
@click.argument("account_email")
@click.argument("ou")
@click.option("--role-name", default="OrgAdminRole", help="Role name for the new account")
def create_account_cmd(account_name, account_email, ou, role_name):
    """Create an AWS account and move it to an OU"""
    try:
        res = create_member_account(account_name, account_email, ou, role_name=role_name)
        click.echo(f"Account created: {res}")
        log_info(f"Account created: {res}")
    except Exception as exc:
        log_error(f"Failed to create account: {exc}")
        raise click.Abort()


@cli.command("list-accounts")
def list_accounts_cmd():
    """List all AWS organization member accounts"""
    try:
        accounts = list_member_accounts()
        click.echo(f"Found {len(accounts)} accounts")
        for acc in accounts:
            click.echo(f"- {acc['Name']} ({acc['Id']}) - {acc['Email']}")
        log_info(f"Listed {len(accounts)} accounts")
    except Exception as exc:
        log_error(f"Failed to list accounts: {exc}")
        raise click.Abort()


@cli.command("get-account")
@click.argument("account_id")
def get_account_cmd(account_id):
    """Get details for a specific AWS account"""
    try:
        account = get_account_details(account_id)
        click.echo(f"Account details: {account}")
        log_info(f"Retrieved details for account {account_id}")
    except Exception as exc:
        log_error(f"Failed to get account details: {exc}")
        raise click.Abort()


@cli.command("move-account")
@click.argument("account_id")
@click.argument("destination_ou")
def move_account_cmd(account_id, destination_ou):
    """Move account to another OU"""
    try:
        res = move_account_to_ou(account_id, destination_ou)
        click.echo(f"Account moved successfully: {res}")
        log_info(f"Moved account {account_id} to OU {destination_ou}")
    except Exception as exc:
        log_error(f"Failed to move account: {exc}")
        raise click.Abort()


@cli.command("close-account")
@click.argument("account_id")
def close_account_cmd(account_id):
    """Close an AWS member account"""
    try:
        success = close_member_account(account_id)
        if success:
            click.echo(f"Account {account_id} closed successfully")
            log_info(f"Closed account {account_id}")
        else:
            click.echo(f"Failed to close account {account_id}")
    except Exception as exc:
        log_error(f"Error closing account: {exc}")
        raise click.Abort()


if __name__ == "__main__":
    cli()







# import click
# from aws_auto.organizational_unit import create_organizational_unit
# from aws_auto.account import create_member_account
# from aws_auto.log_handler import log_info, log_error

# @click.group()
# def cli():
#     """aws_auto OU & Account automation CLI"""
#     pass

# @cli.command("create-ou")
# @click.argument("ou_name")
# def create_ou_cmd(ou_name):
#     """Create an Organizational Unit"""
#     try:
#         res = create_organizational_unit(ou_name)
#         log_info(f"OU created or found: {res}")
#     except Exception as exc:
#         log_error(f"Failed to create OU: {exc}")
#         raise click.Abort()

# @cli.command("create-account")
# @click.argument("account_name")
# @click.argument("account_email")
# @click.argument("ou")
# @click.option("--role-name", default="OrgAdminRole", help="Role name to create in the new account")
# def create_account_cmd(account_name, account_email, ou, role_name):
#     """Create an AWS account and move into OU"""
#     try:
#         res = create_member_account(account_name, account_email, ou, role_name=role_name)
#         log_info(f"Account created: {res}")
#     except Exception as exc:
#         log_error(f"Failed to create account: {exc}")
#         raise click.Abort()

# if __name__ == "__main__":
#     cli()
