# Задача - Декоратор управления доступом

import functools

current_role = "admin"


def access_control(roles: list[str]):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if current_role in roles:
                return func(*args, **kwargs)
            else:
                raise PermissionError

        return wrapper

    return decorator
