from functools import wraps, partial
from multiprocessing import cpu_count

import numpy as np
from tqdm.contrib.concurrent import thread_map


def enable_threading(name=''):
    """Decorator enabling multithreaded analysis.

    It can be applied to any analysis function that operates in a single
    iteration, and it will extend it to be able to analyze several
    iterations at once using multithreading if the `iterations`
    given by the user are an array or list.

    Parameters
    ----------
    name : str, optional
        Name of the analyzed parameter, by default ''
    """
    def threading_decorator(func):
        @wraps(func)
        def run_with_threading(self, iteration, **kwargs):
            if isinstance(iteration, (list, np.ndarray)):
                part_func = partial(func, self, **kwargs)
                tqdm_params = {'ascii': True, 'desc': f'Analyzing {name}... '}
                n_proc = cpu_count()
                ts_params = thread_map(part_func, iteration,
                                       max_workers=n_proc, **tqdm_params)
                return ts_params
            else:
                return func(self, iteration, **kwargs)
        return run_with_threading
    return threading_decorator
