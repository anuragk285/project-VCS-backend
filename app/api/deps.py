from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import TokenError, decode_access_token
from app.models import User, UserRoles

# Shows an "Authorize" button in /docs where you paste the access_token from /auth/login.
bearer_scheme = HTTPBearer(auto_error=False, description="Paste the access_token from POST /auth/login")


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """The signed-in user, or a 401 error. Use it in any route that needs a login."""

    def unauthorized(message: str) -> HTTPException:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, message, headers={"WWW-Authenticate": "Bearer"})

    if credentials is None:
        raise unauthorized("Not signed in")
    try:
        claims = decode_access_token(credentials.credentials)
        user = db.get(User, int(claims["sub"]))
    except TokenError as error:
        raise unauthorized(str(error)) from error
    except ValueError as error:  # the subject was not a number
        raise unauthorized("Token is not valid") from error
    if user is None or not user.is_active:  # the database decides: a disabled user is out at once
        raise unauthorized("Not signed in")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: UserRoles):
    """Builds a dependency that lets in only users with one of these roles."""

    def check_role(user: CurrentUser) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to do that"
            )
        return user

    return check_role


require_customer = require_role(UserRoles.customer)
require_merchant = require_role(UserRoles.merchant)


CurrentCustomer = Annotated[User, Depends(require_customer)]


CurrentMerchant = Annotated[User, Depends(require_merchant)]

