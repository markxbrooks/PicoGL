import cProfile
import io
import pstats
from functools import wraps
from typing import Callable, Optional

from decologr import Decologr as log  # Or replace with `import logging`


def function_profiler(
    _func: Optional[Callable] = None, *, sortby: str = "cumtime", top_n: int = 50
):
    """
    A decorator to profile function performance. Can be used with or without arguments.

    Usage:
        @function_profiler
        def my_func(): ...

        @function_profiler(sortby='tottime', top_n=25)
        def another_func(): ...

    :param _func: Internal placeholder for decorator usage without parameters.
    :param sortby: str - Sorting key for profiling ('cumtime', 'tottime', etc).
    :param top_n: int - Number of top functions to show in profile output.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats(top_n)

            log.message(f"📊 Profiling results for {func.__name__}:\n{s.getvalue()}")
            return result

        return wrapper

    # Handle both @decorator and @decorator(...)
    if _func is None:
        return decorator
    else:
        return decorator(_func)


def function_profiler_old(sortby="cumtime", top_n=50):
    """
    Decorator to profile a function and log its performance.

    :param sortby: str - Sorting criteria for profiling results ('cumtime' or 'tottime').
    :param top_n: int - Number of top entries to display in the profiling results.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()  # Start profiling

            # Execute the wrapped function
            result = func(*args, **kwargs)

            profiler.disable()  # Stop profiling

            # Process profiling results
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats(top_n)  # Print the top N entries

            # Log the profiling results (replace with your logging mechanism)
            log.message(f"Profiling results for {func.__name__}:\n{s.getvalue()}")

            return result

        return wrapper

    return decorator
