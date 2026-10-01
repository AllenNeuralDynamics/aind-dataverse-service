"""Module to handle Dataverse sessions."""

from azure.core.credentials import AccessToken


class StaticTokenCredential:
    """
    An adapter that satisfies the Azure TokenCredential interface
    using a pre-acquired static access token string.
    """

    def __init__(self, access_token: dict):
        """Class constructor."""
        self.access_token = access_token

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        """Returns the AccessToken named tuple required by azure-core"""
        return AccessToken(
            self.access_token["token"], self.access_token["expires_on"]
        )
