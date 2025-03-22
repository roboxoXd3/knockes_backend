import jwt
from datetime import datetime, timedelta
from raininfotech import settings
from users.models import UserTokenLog


def create_token512(user):
    payload = {
        "sub": str(user.id),
        "iat": datetime.now(),
        "exp": datetime.now() + timedelta(days=7),
    }

    decodedJwt = "2f." + encodeJwt(payload)

    # User login logs
    user_token_log(user.id, decodedJwt)

    encodedJwt = decodedJwt
    return encodedJwt


def encodeJwt(payload):
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS512")


def user_token_log(user_id, token, is_block=0):
    try:
        # Create a log entry for the token
        user_log = UserTokenLog.objects.create(
            user_id=user_id,
            user_token=token,
            is_block=is_block,
        )
        user_log.save()
    except Exception as e:
        print(f"Error logging token: {e}")
