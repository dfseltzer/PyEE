from functools import wraps

def state_check(*vars_required):
    """
    Decorator to ensure required state vars exist before calling the method.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # use passed state, or if that does not exist use  class instance state...
            state = kwargs.get("state", None)
            if state is None:
                state = getattr(self, "state", None)

            if state is None:
                raise ValueError(f"Unable to find non-None state dictionary for object!")

            # verify that required state values exist...
            missing = [v for v in vars_required if v not in state or state[v] is None]
            if missing:
                raise ValueError(f"Missing or None state values for: {', '.join(missing)}")

            # if ok, use the state dict we found...
            kwargs["state"] = state

            # finally call the function with the new state dict and all other arguments.
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
