from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

try:
    w.secrets.create_scope(scope="database")
except Exception:
    print("Secret scope already exists")

w.secrets.put_secret(
    scope="database",
    key="support-lakebase-url",
    string_value=getpass.getpass("Paste your Lakebase URL: ")
)

w.secrets.put_acl(
    scope="database",
    principal="users",
    permission=workspace.AclPermission.READ,
)