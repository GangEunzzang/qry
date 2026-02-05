"""Secure password storage using OS keyring."""

import keyring

SERVICE_NAME = "qry"


class KeyringService:
    """Manages secure password storage using OS keyring."""

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        """Initialize keyring service.

        Args:
            service_name: Service name for keyring storage.
        """
        self._service_name = service_name

    def save_password(self, connection_name: str, password: str) -> None:
        """Save password securely.

        Args:
            connection_name: Connection identifier.
            password: Password to store.
        """
        keyring.set_password(self._service_name, connection_name, password)

    def get_password(self, connection_name: str) -> str | None:
        """Retrieve stored password.

        Args:
            connection_name: Connection identifier.

        Returns:
            Stored password or None if not found.
        """
        return keyring.get_password(self._service_name, connection_name)

    def delete_password(self, connection_name: str) -> None:
        """Delete stored password.

        Args:
            connection_name: Connection identifier.
        """
        try:
            keyring.delete_password(self._service_name, connection_name)
        except keyring.errors.PasswordDeleteError:
            pass  # Password doesn't exist
