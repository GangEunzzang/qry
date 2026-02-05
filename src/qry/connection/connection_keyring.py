"""Secure password storage using OS keyring."""

import keyring

SERVICE_NAME = "qry"


class KeyringService:
    """Manages secure password storage using OS keyring."""

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        self._service_name = service_name

    def save_password(self, connection_name: str, password: str) -> None:
        keyring.set_password(self._service_name, connection_name, password)

    def get_password(self, connection_name: str) -> str | None:
        return keyring.get_password(self._service_name, connection_name)

    def delete_password(self, connection_name: str) -> None:
        try:
            keyring.delete_password(self._service_name, connection_name)
        except keyring.errors.PasswordDeleteError:
            pass
