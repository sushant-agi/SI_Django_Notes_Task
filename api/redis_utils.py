from django.core.cache import cache


def is_rate_limited(key, limit, window):
    count = cache.get(key, 0)

    if count >= limit:
        return True

    cache.set(
        key,
        count + 1,
        timeout=window
    )

    return False