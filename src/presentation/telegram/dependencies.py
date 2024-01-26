from inspect import Parameter

from dishka import AsyncContainer, wrap_injection


def inject(func):
    getter = lambda kwargs: kwargs["container"]
    additional_params = [
        Parameter(
            name="container",
            annotation=AsyncContainer,
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
