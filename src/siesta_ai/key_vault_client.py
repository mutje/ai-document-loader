import os 
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class KeyVaultClient(SecretClient):
    def __init__(self, key_vault_name):
        key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
        credential = DefaultAzureCredential()
        super().__init__(key_vault_uri, credential)

    def get_app_setting(self, name: str) -> str:
        return self.get_secret(f"AppSettings-{name}").value

    def get_app_settings(self, names: list) -> dict:
        return dict([(name, self.get_app_setting(name)) for name in names])