import datetime
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas.user import RegisterUserRequest,LoginUser
from app.models.user import User
from app.auth.hashing import (
    encryptPassword,
    verify_password,
    password_is_strong,
    verify_token,
    create_access_token,
    create_refresh_token
)
from app.config.email import send_account_verification_email



async def create_user(user: RegisterUserRequest, session: Session):
    try:
        # Check if the user already exists
        user_exist = session.query(User).filter(User.email == user.email).first()
        if user_exist:
            raise HTTPException(status_code=400, detail="User already exists")

        # Validate password strength
        if not password_is_strong(user.password):
            raise HTTPException(
                status_code=400, detail="Please provide a stronger password"
            )

        # Create new user
        new_user = User(
            name=user.name,
            email=user.email,
            password=encryptPassword(user.password),  # Hash password
            is_active=False,
        )

        # Add and commit the new user to the database
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Send verification email
        await send_account_verification_email(
            recipients=[new_user.email], email=new_user.email
        )

        # Return the newly created user
        return new_user

    except Exception as e:
        # Rollback the session if any error occurs
        session.rollback()

        # Raise an HTTPException with a generic error message
        raise HTTPException(status_code=500, detail="Failed to create user. Please try again later.")
    finally:
        # Ensure the session is closed
        session.close()


# user verification
# transaction issue- despite error data write was persisted instead of aborted
# is it safe to pass token in url?
# document code. you eaily forget the steps
async def verify_registered_user(email: str, session: Session, token: str):
    try:
        # Retrieve user by email
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        # Verify the token
        verification_status = verify_token(token=token, user_email=email)
        print(verification_status)
        
        if verification_status == 'Invalid token':
            raise HTTPException(status_code=400, detail="Invalid token")
        
        if verification_status == 'token expired':
            raise HTTPException(status_code=400, detail="Expired token")
        
        if not verification_status:
            raise HTTPException(status_code=400, detail="User verification failed")

        # Update user verification status
        user.verified_at = datetime.now()
        user.is_active = True
        session.commit()  # Commit the transaction only if everything is successful

        # Return success response
        return JSONResponse(
            status_code=200, content={"message": "Account activated. You can now log in."}
        )

    except Exception as e:
        session.rollback()  # Roll back the transaction if any error occurs
        raise e  # Re-raise the exception to be handled by FastAPI
    finally:
        session.close()  # Ensure the session is closed


# user login
async def login_user(user: LoginUser, session: Session):
    """
    Authenticates a user and generates access and refresh tokens.

    This function takes a user's login details, verifies the credentials against
    the stored information in the database, and generates JWT tokens for authentication.
    If the user is not found or the password is incorrect, an HTTPException is raised.

    Args:
        user (LoginUser): The user login data containing email and password.
        session (Session): The database session used to query the user.

    Returns:
        dict: A dictionary containing the generated access and refresh tokens, 
              along with the token type. The structure is as follows:
              {
                  "access_token_expires": str,   # JWT access token, expires in 15 minutes
                  "refresh_token_expires": str,  # JWT refresh token, expires in 7 days
                  "token_type": "bearer"
              }

    Raises:
        HTTPException: 
            - 400 Bad Request: If the user is not found or the password is incorrect.
            - 500 Internal Server Error: If there is a failure during the login process.
    
    Example:
        Example usage of the function:
        
        ```python
        try:
            login_response = await login_user(user_data, db_session)
            print("Login successful:", login_response)
        except HTTPException as e:
            print("Login failed:", e.detail)
        ```

    Note:
        The `LoginUser` model should contain `email` and `password` fields, and the
        `User` model should have matching columns in the database. Make sure the password
        verification function (`verify_password`) and token creation functions
        (`create_access_token`, `create_refresh_token`) are implemented correctly.
    """
    try:
        # Query the user from the database
        login_user = session.query(User).filter(User.email == user.email).first()

        # if user not found in database raise exception
        if not login_user:
            raise HTTPException(status_code=400, detail="User not found")

        # Verify the password
        password = encryptPassword(password=user.password)
        is_password_correct = verify_password(password, login_user.password)
        if not is_password_correct:
            raise HTTPException(status_code=400, detail="Wrong Password")

        # Generate access and refresh tokens
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email}, expires_delta=timedelta(days=7)
        )

        # Return the tokens
        return {
            "access_token_expires": access_token,
            "refresh_token_expires": refresh_token,
            "token_type": "bearer"
        }

    except Exception as e:
        # Rollback the session if any error occurs (although not strictly needed here since no changes are made)
        session.rollback()

        # Raise an HTTPException with a user-friendly error message
        raise HTTPException(status_code=500, detail="Failed to log in. Please try again later.")
    finally:
        # Close the session
        session.close()
    

