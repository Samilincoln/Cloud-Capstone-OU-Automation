# Cloud-Capstone-OU-Automation

This project provides a set of Python scripts and a Flask API for automating the creation and management of AWS Organizations, Organizational Units (OUs), and member accounts. It leverages `boto3` for AWS interactions and `python-dotenv` for environment variable management.

## Project Structure and High-Level Documentation

### `create_account.py`

This script is designed to create new AWS member accounts within an existing Organizational Unit (OU). It can be used as an importable function or run directly via the command line for testing. It leverages temporary credentials, performs OU lookups, initiates account creation, and moves the newly created account to the specified OU.

**Functions:**

*   **`resolve_ou_id(org_client, *, ou_name: str = None, ou_id: str = None) -> str`**:
    *   **Purpose**: This helper function resolves an Organizational Unit (OU) to its corresponding ID.
    *   **Parameters**:
        *   `org_client`: An initialized `boto3` Organizations client.
        *   `ou_name` (optional): The name of the OU.
        *   `ou_id` (optional): The ID of the OU (e.g., "ou-xxxx-xxxxxxxx").
    *   **Behavior**:
        *   If `ou_id` is provided, it's returned directly.
        *   If `ou_name` is provided, it searches for the OU under the organization's root and returns its ID.
        *   If neither `ou_name` nor `ou_id` is provided, or if the `ou_name` is not found, it raises a `ValueError`.

*   **`create_member_account(account_name: str, account_email: str, ou: str, role_name: str = "OrgAdminRole", *, _debug: bool = False) -> Dict[str, Any]`**:
    *   **Purpose**: This is the main function for creating a new AWS member account and placing it into a specified OU.
    *   **Parameters**:
        *   `account_name`: The desired name for the new AWS account.
        *   `account_email`: A unique email address for the new AWS account.
        *   `ou`: The target Organizational Unit. This can be either the OU's name or its ID.
        *   `role_name` (optional): The IAM role name to be created in the new account (defaults to "OrgAdminRole").
        *   `_debug` (optional): A boolean flag to enable debug output (defaults to `False`).
    *   **Behavior**:
        1.  **Get Temporary Credentials**: Obtains temporary credentials using `setup_org_and_get_creds` from `credential_and_role.py`.
        2.  **Resolve OU**: Determines the target OU's ID, automatically detecting if the `ou` parameter is a name or an ID.
        3.  **Start Account Creation**: Initiates the AWS account creation process using `org_client.create_account`. It handles cases where account creation might already be in progress.
        4.  **Wait for Completion**: Polls the `org_client.describe_create_account_status` until the account creation succeeds or fails.
        5.  **Move to OU**: Once the account is created, it moves the account from the organization's root to the specified target OU using `org_client.move_account`.
        6.  **Return Result**: Returns a dictionary containing details of the newly created account, including its ID, name, email, OU ID, and the temporary credentials used.

### `create_ou.py`

This script is responsible for creating new Organizational Units (OUs) within AWS Organizations. It utilizes temporary credentials to interact with the AWS Organizations service.

**Functions:**

*   **`create_organizational_unit(ou_name: str, role_name: str = "OrgAdminRole") -> dict`**:
    *   **Purpose**: Creates a new Organizational Unit (OU) in AWS Organizations.
    *   **Parameters**:
        *   `ou_name`: The name of the OU to be created.
        *   `role_name` (optional): The IAM role name to use for obtaining temporary credentials (defaults to "OrgAdminRole").
    *   **Behavior**:
        1.  **Get Temporary Credentials**: Obtains temporary credentials using `setup_org_and_get_creds` from `credential_and_role.py`.
        2.  **Create Session**: Establishes a `boto3` session using the temporary credentials.
        3.  **Get Root Parent**: Retrieves the ID of the organization's root.
        4.  **Create OU**: Attempts to create the OU using `org_client.create_organizational_unit`.
        5.  **Handle Duplicates**: If an OU with the same name already exists, it reuses the existing OU's ID instead of raising an error.
        6.  **Return Result**: Returns a dictionary containing the OU's name, ID, and the temporary credentials used.

### `credential_and_role.py`

This script handles the setup of AWS Organizations, the creation or retrieval of an IAM role, and the assumption of that role to obtain temporary AWS credentials. It's a crucial component for other scripts that need to interact with AWS Organizations.

**Functions:**

*   **`get_client(service, region=None)`**:
    *   **Purpose**: A helper function to create a `boto3` client with a predefined configuration (retries, timeouts, and default region).
    *   **Parameters**:
        *   `service`: The AWS service name (e.g., 'sts', 'organizations', 'iam').
        *   `region` (optional): The AWS region to use for the client (defaults to 'us-east-1').
    *   **Behavior**: Returns a configured `boto3` client for the specified service.

*   **`setup_org_and_get_creds(role_name: str) -> dict`**:
    *   **Purpose**: Ensures an AWS Organization exists, creates or retrieves a specified IAM role, assumes that role, and returns temporary AWS credentials.
    *   **Parameters**:
        *   `role_name`: The name of the IAM role to create or assume.
    *   **Behavior**:
        1.  **Get Account ID**: Retrieves the AWS account ID of the caller.
        2.  **Ensure Organization Exists**: Checks if an AWS Organization exists. If not, it creates one. It also handles `AccessDeniedException` if the credentials are not from the management account.
        3.  **Create or Get IAM Role**: Attempts to create an IAM role with the given `role_name` and a predefined trust policy. If the role already exists, it proceeds without error. It then attaches the `AWSOrganizationsFullAccess` policy to the role.
        4.  **Assume Role**: Assumes the created/retrieved IAM role using `sts_client.assume_role` to obtain temporary security credentials.
        5.  **Build Result**: Returns a dictionary containing the role details, account ID, organization ID, and the temporary `access_key_id`, `secret_access_key`, `session_token`, and their expiration.

### `flask_endpoint.py`

This Flask application provides an API endpoint to retrieve temporary AWS credentials for interacting with the AWS Organizations API. It reuses the logic from `credential_and_role.py` to ensure an organization exists and a specific IAM role is available, then assumes that role to provide temporary credentials.

**Functions:**

*   **`get_client(service, region=None)`**:
    *   **Purpose**: A helper function to create a `boto3` client with a predefined configuration (retries, timeouts, and default region). This is identical to the function in `credential_and_role.py`.
    *   **Parameters**:
        *   `service`: The AWS service name (e.g., 'sts', 'organizations', 'iam').
        *   `region` (optional): The AWS region to use for the client (defaults to 'us-east-1').
    *   **Behavior**: Returns a configured `boto3` client for the specified service.

*   **`setup_org_and_get_creds(role_name: str) -> dict`**:
    *   **Purpose**: Ensures an AWS Organization exists, creates or retrieves a specified IAM role, assumes that role, and returns temporary AWS credentials. This function is a slightly modified version of the one in `credential_and_role.py`, with some error handling adjusted for the API context.
    *   **Parameters**:
        *   `role_name`: The name of the IAM role to create or assume.
    *   **Behavior**:
        1.  **Get Account ID**: Retrieves the AWS account ID of the caller.
        2.  **Ensure Organization Exists**: Checks if an AWS Organization exists. If not, it creates one. It raises a `PermissionError` if the credentials are not from the management account when trying to create an organization.
        3.  **Create or Reuse Role**: Attempts to create an IAM role with the given `role_name` and a trust policy that allows the root account to assume it. If the role already exists, it proceeds. It then attaches the `AWSOrganizationsFullAccess` policy to the role.
        4.  **Assume Role**: Assumes the created/retrieved IAM role to obtain temporary security credentials.
        5.  **Return Dict**: Returns a dictionary containing the role details, account ID, organization ID, and the temporary `access_key_id`, `secret_access_key`, `session_token`, and their expiration.

*   **`get_aws_creds()`**:
    *   **Purpose**: This is a Flask API endpoint (`/get-aws-creds`) that provides temporary AWS credentials.
    *   **Parameters**: Expects `role_name` either as a query parameter or in the JSON body of a POST request.
    *   **Behavior**:
        *   Retrieves the `role_name` from the request.
        *   Calls `setup_org_and_get_creds` with the provided `role_name`.
        *   Returns the temporary credentials as a JSON response.
        *   Handles `PermissionError` (403 Forbidden) and other exceptions (500 Internal Server Error).

*   **`health()`**:
    *   **Purpose**: A simple health check endpoint (`/health`).
    *   **Parameters**: None.
    *   **Behavior**: Returns a JSON response `{"status": "ok"}` to indicate the API is running.

### `organization_creation.py`

This script is designed to create an AWS Organization or retrieve details of an existing one. It's primarily used for initial setup and verification of the AWS Organizations service.

**Functions:**

*   **`get_org_client()`**:
    *   **Purpose**: Configures and returns a `boto3` client for the AWS Organizations service.
    *   **Parameters**: None.
    *   **Behavior**: Returns a `boto3` Organizations client, explicitly set to the `us-east-1` region (as AWS Organizations operates globally but is managed from `us-east-1`), with retry and timeout configurations.

*   **`create_aws_organization(client)`**:
    *   **Purpose**: Creates a new AWS Organization with all features enabled, or retrieves details of an existing organization if one already exists.
    *   **Parameters**:
        *   `client`: An initialized `boto3` Organizations client.
    *   **Behavior**:
        *   Attempts to create an organization using `client.create_organization(FeatureSet='ALL')`.
        *   If `AlreadyInOrganizationException` occurs, it means an organization already exists, so it retrieves and returns its details using `client.describe_organization()`.
        *   Handles `AccessDeniedException` if the credentials used are not from the root user, which is required for organization creation.
        *   Catches other `ClientError`, `BotoCoreError`, `ConnectionError`, and general exceptions, printing informative error messages.
        *   Returns the organization details (a dictionary) on success, or `None` on failure.

*   **`main()`**:
    *   **Purpose**: The main execution function when the script is run directly.
    *   **Parameters**: None.
    *   **Behavior**:
        *   Prints the ARN of the caller identity for debugging purposes.
        *   Calls `get_org_client()` to get an Organizations client.
        *   Calls `create_aws_organization()` to create or retrieve the organization.
        *   Prints the organization ARN if successful, otherwise prints an error and exits.

### `requirements.txt`

This file lists the Python dependencies required for the project. These packages can be installed using `pip` (e.g., `pip install -r requirements.txt`).

**Dependencies:**

*   **`boto3>=1.34.0`**:
    *   **Purpose**: The Amazon Web Services (AWS) SDK for Python. It allows Python developers to write software that makes use of AWS services like S3, EC2, DynamoDB, and more. The version specified is `1.34.0` or newer.

*   **`python-dotenv`**:
    *   **Purpose**: This library reads key-value pairs from a `.env` file and sets them as environment variables. This is commonly used for managing configuration variables (like AWS credentials) separately from the codebase.