import os
from functools import wraps, partial
from multiprocessing import cpu_count

import numpy as np
from tqdm.contrib.concurrent import thread_map, process_map


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
                ts_params = np.array(ts_params)
                if ts_params.ndim == 1:
                    return ts_params
                else:
                    out = []
                    num_outputs = ts_params.shape[1]
                    for i in range(num_outputs):
                        out.append(np.ascontiguousarray(ts_params[:, i]))
                    return (*out,)
            else:
                return func(self, iteration, **kwargs)
        return run_with_threading
    return threading_decorator


# Solution for a multiprocessing decorator based on
# https://stackoverflow.com/questions/70002454/how-to-implement-a-
# multiprocessing-python-decorator
original_functions={}


def func_runner(name, *args, **kwargs):
    return original_functions[name](*args, **kwargs)


def enable_multiprocessing(name=''):
    """Decorator enabling parallel analysis with multiprocessing.

    It can be applied to any analysis function that operates in a single
    iteration, and it will extend it to be able to analyze several
    iterations at once using multiprocessing if the `iterations`
    given by the user are an array or list.

    Parameters
    ----------
    name : str, optional
        Name of the analyzed parameter, by default ''
    """
    def multiprocessing_decorator(func):
        original_functions[func.__name__] = func
        @wraps(func)
        def run_with_multiprocessing(self, iteration, **kwargs):
            if isinstance(iteration, (list, np.ndarray)):
                part_func = partial(func_runner, func.__name__, self, **kwargs)
                tqdm_params = {'ascii': True, 'desc': f'Analyzing {name}... '}
                n_proc = cpu_count()
                ts_params = process_map(part_func, iteration,
                                        max_workers=n_proc, **tqdm_params)
                ts_params = np.array(ts_params)
                if ts_params.ndim == 1:
                    return ts_params
                else:
                    out = []
                    num_outputs = ts_params.shape[1]
                    for i in range(num_outputs):
                        out.append(np.ascontiguousarray(ts_params[:, i]))
                    return (*out,)
            else:
                return func(self, iteration, **kwargs)
        return run_with_multiprocessing
    return multiprocessing_decorator


enable_parallelism = enable_threading
if 'VP_ENABLE_MULTIPROCESSING' in os.environ:
    if int(os.environ['VP_ENABLE_MULTIPROCESSING']) == 1:
        enable_parallelism = enable_multiprocessing
