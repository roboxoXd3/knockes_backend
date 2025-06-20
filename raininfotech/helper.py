import re
import jwt
from django.core.cache import cache
from datetime import datetime, timedelta, timezone
from raininfotech import settings
from users.models import UserTokenLog


def email_validation(email):
    regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    if re.search(regex, email):
        return True
    return False


def create_token(user):
    access_payload = {
        "sub": str(user.id),
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),  # Short-lived access token
    }

    refresh_payload = {
        "sub": str(user.id),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRY_DAY),  # Long-lived refresh token
    }

    access_token = "2f." + encodeJwt(access_payload)
    refresh_token = "2f." + encodeJwt(refresh_payload)

    # Log token generation
    user_token_log(user.id, access_token)

    return {
        "access": access_token,
        "refresh": refresh_token,
    }


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


def decodeJwt(encoded, verify=True):
    encoded = encoded[3:]  # remove "2f." prefix
    try:
        return jwt.decode(
            encoded,
            settings.SECRET_KEY,
            algorithms=["HS512"],
            options={"verify_aud": False, "require_sub": True},
        )
    except jwt.ExpiredSignatureError:
        print("⚠️ Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
        return None


def cache_set(key, value, expiry=300):
    cache.set(key, value, timeout=expiry)
