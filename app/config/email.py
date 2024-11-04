from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.auth.hashing import create_token

import os
from app.config.settings import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
    MAIL_FROM=os.environ.get("MAIL_FROM", "noreply@test.com"),
    MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME", settings.APP_NAME),
    MAIL_PORT=os.environ.get("MAIL_PORT", 1025),
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp"),
    MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS", "False"),
    MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS", "False"),
    MAIL_DEBUG=True,
    USE_CREDENTIALS=os.environ.get("USE_CREDENTIALS", "True"),
)


fm = FastMail(conf)


async def send_account_verification_email(recipients: list, email:str):
    # function takes in list of recipients and the email of newly created user for verification logic
    token = create_token(user=email)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head></head>
    <body>
        <p>Hello, click on this link to verify your account:</p>
        <p><a href="http://localhost:8000/users/verify/?token={token}&email={email}">Verify Account</a></p>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Describly- Account Verification",
        recipients=recipients,
        body=html,
        subtype=MessageType.html,
    )
    await fm.send_message(message)

    return JSONResponse(status_code=200, content={"message": "Sent"})


# backgroundtasks
# token exoiration
# restructure
