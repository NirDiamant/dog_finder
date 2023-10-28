from configparser import ConfigParser
import os
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer

def get_auth0_config():
    """Sets up configuration for the app"""

    env = os.getenv("ENV", ".config")

    # Read config from .config file or environment variables
    if env == ".config":
        config = ConfigParser()
        config.read(".config")
        config = config["AUTH0"]
    else:
        config = {
            "DOMAIN": os.getenv("AUTH0_DOMAIN"),
            "API_AUDIENCE": os.getenv("AUTH0_API_AUDIENCE"),
            "ISSUER": os.getenv("AUTH0_ISSUER"),
            "ALGORITHMS": os.getenv("AUTH0_ALGORITHMS"),
        }
    for key, value in config.items():
        if value == "":
            print(f"Missing config: {key}")
            exit(1)
    return config

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


class VerifyToken:
    def __init__(self):
        # Fetch Auth0 configuration data
        self.config = get_auth0_config()

        # Construct the JWKS URL from the provided domain in the Auth0 config
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        # Create a JWK client to fetch the signing keys for JWT verification
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(self,
                     security_scopes: SecurityScopes,
                     token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())
                     ):
        # If no token is provided, raise an exception indicating lack of authentication
        if token is None:
            raise UnauthenticatedException

        try:
            # Fetch the signing key associated with the provided JWT
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        # Handle exceptions related to JWKS client or JWT decoding errors
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error))
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error))

        try:
            # Decode and verify the JWT using the fetched signing key
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        # Handle exceptions related to JWT decoding
        except Exception as error:
            raise UnauthorizedException(str(error))

        # Check if there are any specific security scopes to verify
        if len(security_scopes.scopes) > 0:
            permissions = payload["permissions"]
            for required_permission in security_scopes.scopes:
                if required_permission not in permissions:
                    raise UnauthorizedException(detail=f'Missing "{required_permission}" permission')


        return payload
