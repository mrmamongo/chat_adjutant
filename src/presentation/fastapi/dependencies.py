from inspect import Parameter
from typing import get_type_hints

from dishka import wrap_injection
from starlette.requests import Request


def inject(func):
    hints = get_type_hints(func)
    requests_param = next(
        (name for name, hint in hints.items() if hint is Request),
        None,
    )
    if requests_param:
        getter = lambda kwargs: kwargs[requests_param].state.container
        additional_params = []
    else:
        getter = lambda kwargs: kwargs["___r___"].state.container
        additional_params = [
            Parameter(
                name="___r___",
                annotation=Request,
                kind=Parameter.KEYWORD_ONLY,
            )
        ]

    return wrap_injection(
        func=func,
        remove_depends=True,
        container_getter=getter,
        additional_params=additional_params,
        is_async=True,
    )
