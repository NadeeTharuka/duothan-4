from datetime import timedelta

from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from dtp.dtp_token import generate_dtp_token
from models.user_model import UserInDB

from auth.authorize import authenticate_user, oauth2_scheme
from auth.hashing import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, blacklist_token
from services.user_service import user_exists, get_next_avail_id, add_new_user

"""
    API router for auth endpoint
    
    Attributes:
        router (APIRouter): the router for the endpoint

    Methods:
        [POST] /api/auth/register
        register_user: the endpoint for registering a new user

        [POST] /api/auth/login
        login_for_access_token: the endpoint for logging in a user

        [POST] /api/auth/logout
        logout: the endpoint for logging out a user
"""

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"description": "The requested uri was not found"}},
)


@router.post("/register")
async def register_user(
        first_name: str = Form(...),
        last_name: str = Form(...),
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        mobile: str = Form(...),
        is_admin=False
):
    """
    The endpoint for registering a new user

    Returns:
        (UserInDB) The user that was registered

    Raises:
        HTTPException: if the username already exists

    :param is_admin:
    :param password:
    :param email:
    :param username:
    :param first_name:
    :param last_name:
    :param mobile:

    """
    if user_exists(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    hashed_password = get_password_hash(password)

    dtp_token = generate_dtp_token()

    user = UserInDB(
        id=get_next_avail_id(),
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin,
        mobile=mobile,
        first_name=first_name,
        last_name=last_name,
        dtp_token=dtp_token
    )
    add_new_user(user)

    return {"user": user, "dtp_token": dtp_token}


@router.post("/login")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    The endpoint for logging in a user

    Args:
        form_data (OAuth2PasswordRequestForm): the form data for the user

    Returns:
        (dict) The access token for the user

    Raises:
        HTTPException: if the username or password is incorrect
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires.seconds
        # Unresolved attribute reference 'username' for class 'bool'
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    The endpoint for logging out a user

    Args:
        token (oauth2 bearer token): the token for the user

    Returns:
        (dict) The message for logging out
    """
    blacklist_token(token)
    return {"message": "Successfully logged out"}
