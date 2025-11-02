# Cloud-Capstone-OU-Automation

This project provides a robust solution for automating the management of AWS Organizations, Organizational Units (OUs), and member accounts. It leverages `boto3` for AWS API interactions and `python-dotenv` for secure environment variable management, offering both a command-line interface (CLI) and a modular Python API.

## Quickstart

To get started with this project, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/Cloud-Capstone-OU-Automation.git
    cd Cloud-Capstone-OU-Automation
    ```

2.  **Set up a virtual environment**:
    ```bash
    python -m venv venv
    ./venv/Scripts/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure AWS Credentials**:
    Create a `.env` file in the root directory of the project and add your AWS credentials. Ensure the IAM user or role associated with these credentials has the necessary permissions to manage AWS Organizations.

    ```
    AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION=us-east-1
    ```

    Alternatively, you can configure your AWS credentials using the AWS CLI:
    ```bash
    aws configure
    ```

## CLI Usage

The project provides a command-line interface for easy interaction. All CLI commands are prefixed with `aws_auto`.

### Organizational Unit Commands

*   **`aws_auto create-ou <ou_name>`**
    *   **Function**: Creates a new Organizational Unit (OU) or reuses an existing one if it already exists.
    *   **Parameters**:
        *   `<ou_name>` (argument): The name of the Organizational Unit to create.
    *   **Example**:
        ```bash
        aws_auto create-ou Development
        ```

*   **`aws_auto get-ou <ou_name>`**
    *   **Function**: Retrieves the ID of an Organizational Unit by its name.
    *   **Parameters**:
        *   `<ou_name>` (argument): The name of the OU to retrieve the ID for.
    *   **Example**:
        ```bash
        aws_auto get-ou Development
        ```

*   **`aws_auto list-root`**
    *   **Function**: Lists the ID of the root Organizational Unit in the AWS Organization.
    *   **Parameters**: None.
    *   **Example**:
        ```bash
        aws_auto list-root
        ```

### Account Commands

*   **`aws_auto create-account <account_name> <account_email> <ou> [--role-name <role_name>]`**
    *   **Function**: Creates a new AWS member account and moves it into a specified Organizational Unit.
    *   **Parameters**:
        *   `<account_name>` (argument): The desired name for the new AWS account.
        *   `<account_email>` (argument): A unique email address for the new AWS account.
        *   `<ou>` (argument): The target Organizational Unit (can be OU name or OU ID).
        *   `--role-name <role_name>` (option): The IAM role name to be created in the new account (defaults to "OrgAdminRole").
    *   **Example**:
        ```bash
        aws_auto create-account "Dev Account" dev@example.com Development --role-name CustomAdminRole
        ```

*   **`aws_auto list-accounts`**
    *   **Function**: Lists all AWS member accounts within the organization.
    *   **Parameters**: None.
    *   **Example**:
        ```bash
        aws_auto list-accounts
        ```

*   **`aws_auto get-account <account_id>`**
    *   **Function**: Retrieves detailed information for a specific AWS account.
    *   **Parameters**:
        *   `<account_id>` (argument): The ID of the AWS account to retrieve details for.
    *   **Example**:
        ```bash
        aws_auto get-account 123456789012
        ```

*   **`aws_auto move-account <account_id> <destination_ou>`**
    *   **Function**: Moves an AWS account to a different Organizational Unit.
    *   **Parameters**:
        *   `<account_id>` (argument): The ID of the AWS account to move.
        *   `<destination_ou>` (argument): The target Organizational Unit (can be OU name or OU ID) where the account will be moved.
    *   **Example**:
        ```bash
        aws_auto move-account 123456789012 Production
        ```

*   **`aws_auto close-account <account_id>`**
    *   **Function**: Closes an AWS member account.
    *   **Parameters**:
        *   `<account_id>` (argument): The ID of the AWS account to close.
    *   **Example**:
        ```bash
        aws_auto close-account 123456789012
        ```

## Importing and Using as a Module

You can import and use the functions directly in your Python scripts.

### `aws_auto.organizational_unit`

*   **`list_root_id(org_client=None)`**
    *   **Use**: Retrieves the ID of the root organizational unit.
    *   **Parameters**:
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organizational_unit import list_root_id
        root_id = list_root_id()
        print(f"Root OU ID: {root_id}")
        ```

*   **`resolve_ou_id(org_client, *, ou_name=None, ou_id=None)`**
    *   **Use**: Resolves an Organizational Unit ID from its name or returns a provided OU ID directly.
    *   **Parameters**:
        *   `org_client`: A boto3 Organizations client.
        *   `ou_name` (optional, keyword-only): The name of the Organizational Unit.
        *   `ou_id` (optional, keyword-only): The ID of the Organizational Unit.
    *   **Example**:
        ```python
        from aws_auto.organizational_unit import resolve_ou_id
        from aws_auto.aws_client import get_client
        org_client = get_client("organizations")
        dev_ou_id = resolve_ou_id(org_client, ou_name="Development")
        print(f"Development OU ID: {dev_ou_id}")
        ```

*   **`create_organizational_unit(ou_name: str, org_client=None)`**
    *   **Use**: Creates a new Organizational Unit under the root. If an OU with the same name already exists, it reuses the existing OU's ID.
    *   **Parameters**:
        *   `ou_name`: The name of the Organizational Unit to create.
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organizational_unit import create_organizational_unit
        new_ou = create_organizational_unit("Testing")
        print(f"Created/Reused OU: {new_ou}")
        ```

*   **`list_organizational_units(org_client=None)`**
    *   **Use**: Lists all Organizational Units under the root.
    *   **Parameters**:
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organizational_unit import list_organizational_units
        ous = list_organizational_units()
        for ou in ous:
            print(f"OU: {ou['Name']} ({ou['Id']})")
        ```

*   **`update_organizational_unit(ou_id: str, new_name: str, org_client=None)`**
    *   **Use**: Renames an existing Organizational Unit.
    *   **Parameters**:
        *   `ou_id`: The ID of the Organizational Unit to rename.
        *   `new_name`: The new name for the Organizational Unit.
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organizational_unit import update_organizational_unit
        updated_ou = update_organizational_unit("ou-xxxxxxxx", "Staging")
        print(f"Updated OU: {updated_ou}")
        ```

*   **`delete_organizational_unit(ou_id: str, org_client=None)`**
    *   **Use**: Deletes an Organizational Unit.
    *   **Parameters**:
        *   `ou_id`: The ID of the Organizational Unit to delete.
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organizational_unit import delete_organizational_unit
        success = delete_organizational_unit("ou-xxxxxxxx")
        if success:
            print("OU deleted successfully.")
        ```

### `aws_auto.account`

*   **`create_member_account(account_name: str, account_email: str, ou: str, role_name: str = "OrgAdminRole")`**
    *   **Use**: Creates a new AWS member account and moves it into the specified OU (by name or ID).
    *   **Parameters**:
        *   `account_name`: The desired name for the new AWS account.
        *   `account_email`: A unique email address for the new AWS account.
        *   `ou`: The target Organizational Unit (can be OU name or OU ID).
        *   `role_name` (optional): The IAM role name to be created in the new account (defaults to "OrgAdminRole").
    *   **Example**:
        ```python
        from aws_auto.account import create_member_account
        new_account = create_member_account("Prod Account", "prod@example.com", "Production")
        print(f"New account created: {new_account}")
        ```

*   **`list_member_accounts(org_client=None)`**
    *   **Use**: Lists all AWS member accounts within the organization.
    *   **Parameters**:
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.account import list_member_accounts
        accounts = list_member_accounts()
        for account in accounts:
            print(f"Account: {account['Name']} ({account['Id']})")
        ```

*   **`get_account_details(account_id: str, org_client=None)`**
    *   **Use**: Retrieves detailed information for a specific AWS account.
    *   **Parameters**:
        *   `account_id`: The ID of the AWS account to retrieve details for.
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.account import get_account_details
        account_details = get_account_details("123456789012")
        print(f"Account details: {account_details}")
        ```

*   **`move_account_to_ou(account_id: str, destination_ou: str, org_client=None)`**
    *   **Use**: Moves an AWS account to a different Organizational Unit.
    *   **Parameters**:
        *   `account_id`: The ID of the AWS account to move.
        *   `destination_ou`: The target Organizational Unit (can be OU name or OU ID) where the account will be moved.
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.account import move_account_to_ou
        move_result = move_account_to_ou("123456789012", "Security")
        print(f"Account move result: {move_result}")
        ```

*   **`close_member_account(account_id: str, org_client=None)`**
    *   **Use**: Closes an AWS member account.
    *   **Parameters**:
        *   `account_id`: The ID of the AWS account to close.
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.account import close_member_account
        success = close_member_account("123456789012")
        if success:
            print("Account closed successfully.")
        ```

### `aws_auto.aws_client`

*   **`get_client(service: str, region: str = None, **kwargs)`**
    *   **Use**: Creates a boto3 client for the specified AWS service with sensible defaults for retries, timeouts, and credentials.
    *   **Parameters**:
        *   `service`: The name of the AWS service (e.g., "organizations", "s3").
        *   `region` (optional): The AWS region to use. Defaults to `AWS_DEFAULT_REGION` environment variable or "us-east-1".
        *   `**kwargs`: Additional keyword arguments to pass to the boto3 client.
    *   **Example**:
        ```python
        from aws_auto.aws_client import get_client
        s3_client = get_client("s3", region="us-west-2")
        ```

### `aws_auto.iam_roles`

*   **`create_or_get_role(role_name: str, trust_principal_arn: str = None)`**
    *   **Use**: Creates an IAM role with a specified name and attaches the `AWSOrganizationsFullAccess` policy. If the role already exists, it retrieves and reuses it.
    *   **Parameters**:
        *   `role_name`: The name of the IAM role to create or get.
        *   `trust_principal_arn` (optional): If provided, sets a specific ARN as the trusted entity for the role.
    *   **Example**:
        ```python
        from aws_auto.iam_roles import create_or_get_role
        role_info = create_or_get_role("MyAutomationRole")
        print(f"Role ARN: {role_info['role_arn']}")
        ```

*   **`assume_role(role_arn: str, session_name: str = "cloud_capstone_session", duration_seconds: int = 3600)`**
    *   **Use**: Assumes an IAM role and returns temporary security credentials.
    *   **Parameters**:
        *   `role_arn`: The Amazon Resource Name (ARN) of the role to assume.
        *   `session_name` (optional): An identifier for the assumed role session. Defaults to "cloud_capstone_session".
        *   `duration_seconds` (optional): The duration, in seconds, for the role session. Defaults to 3600 seconds (1 hour).
    *   **Example**:
        ```python
        from aws_auto.iam_roles import assume_role
        temp_creds = assume_role("arn:aws:iam::123456789012:role/MyAutomationRole")
        print(f"Temporary Access Key: {temp_creds['AccessKeyId']}")
        ```

### `aws_auto.organization`

*   **`get_organization(org_client=None)`**
    *   **Use**: Retrieves details of the AWS Organization.
    *   **Parameters**:
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organization import get_organization
        org_details = get_organization()
        if org_details:
            print(f"Organization ID: {org_details['Id']}")
        ```

*   **`create_organization_if_missing(org_client=None)`**
    *   **Use**: Creates an AWS Organization with all features enabled if one does not already exist. If an organization already exists, it returns its details.
    *   **Parameters**:
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organization import create_organization_if_missing
        org = create_organization_if_missing()
        print(f"Organization: {org['Id']}")
        ```

*   **`update_organization_tags(tags: dict, org_client=None)`**
    *   **Use**: Applies tags to the AWS Organization.
    *   **Parameters**:
        *   `tags`: A dictionary of tags to apply (key-value pairs).
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organization import update_organization_tags
        updated_org = update_organization_tags({"Project": "CloudCapstone"})
        print(f"Updated organization tags: {updated_org}")
        ```

*   **`delete_organization(org_client=None)`**
    *   **Use**: Deletes the AWS Organization. This operation must be performed by the management account.
    *   **Parameters**:
        *   `org_client` (optional): A boto3 Organizations client. If not provided, a new one will be created.
    *   **Example**:
        ```python
        from aws_auto.organization import delete_organization
        if delete_organization():
            print("Organization deleted successfully.")
        ```

### `aws_auto.log_handler`

*   **`log_info(message: str)`**
    *   **Use**: Logs an informational message to both the configured log file and the console.
    *   **Parameters**:
        *   `message`: The informational message string to log.
    *   **Example**:
        ```python
        from aws_auto.log_handler import log_info
        log_info("This is an informational message.")
        ```

*   **`log_error(message: str)`**
    *   **Use**: Logs an error message to both the configured log file and the console, prefixed with "ERROR:".
    *   **Parameters**:
        *   `message`: The error message string to log.
    *   **Example**:
        ```python
        from aws_auto.log_handler import log_error
        log_error("Something went wrong!")
        ```

## API Usage (Flask Endpoint)

The project includes a Flask application that exposes an API for retrieving temporary AWS credentials.

### `api/app.py`

*   **`/get-aws-creds` (POST)**
    *   **Function**: Retrieves temporary AWS credentials by assuming a specified IAM role.
    *   **Request Body**:
        ```json
        {
            "role_name": "YourIAMRoleName"
        }
        ```
    *   **Response**:
        ```json
        {
            "AccessKeyId": "...",
            "SecretAccessKey": "...",
            "SessionToken": "...",
            "Expiration": "..."
        }
        ```
    *   **Example**:
        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"role_name": "OrgAdminRole"}' http://localhost:5000/get-aws-creds
        ```

*   **`/health` (GET)**
    *   **Function**: Basic health check endpoint.
    *   **Response**:
        ```json
        {
            "status": "healthy"
        }
        ```
    *   **Example**:
        ```bash
        curl http://localhost:5000/health
        ```

To run the Flask application:

```bash
export FLASK_APP=aws_auto/api/app.py
flask run
```

## Notes and Best Practices

*   **Permissions**: Ensure the AWS credentials used have the necessary permissions for AWS Organizations, IAM, and STS.
*   **Error Handling**: The module functions include error handling and logging. It's recommended to implement additional error handling in your calling code as needed.
*   **Idempotency**: Many functions are designed to be idempotent (e.g., `create_organizational_unit`, `create_or_get_role`), meaning they can be called multiple times without causing unintended side effects.
*   **Security**: Be cautious with your AWS credentials. Use environment variables or AWS CLI configuration for managing them securely.
*   **Logging**: Review the `aws_creation_log.txt` file for detailed logs of operations.

