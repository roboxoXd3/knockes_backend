import re
import random as r
from django.core.cache import cache
from raininfotech.settings import REDIS_BLACKLIST_EXPIRY_SECONDS


def data_sanitization(raw_html):
    remove_lt = re.sub(r"<", "&lt", str(raw_html))
    remove_gt = re.sub(r">", "&gt", remove_lt)
    clean_data = re.sub(r"[.]", "", remove_gt)
    clean_data = (
        clean_data.replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
    )

    return str(clean_data)


def phone_no_validation(phone_no):
    Pattern = re.compile("^[1-9][0-9]{9}$")
    return Pattern.match(phone_no)


def send_otp_for_two_fa_verification(telephone, msg, platform=None):
    otp = ""
    for _ in range(4):
        otp += str(r.randint(1, 9))
    return otp


def blacklist_token(token):
    cache.set(f"blacklist:{token}", True, timeout=REDIS_BLACKLIST_EXPIRY_SECONDS)


def is_token_blacklisted(token):
    return cache.get(f"blacklist:{token}") is not None
