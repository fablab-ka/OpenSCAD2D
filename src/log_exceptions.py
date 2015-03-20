from __future__ import print_function
import inspect
import sys

# default frame template (see log_exceptions below)
LOG_FRAME_TPL = '  File "%s", line %i, in %s\n    %s\n'


# log_exceptions decorator
def log_exceptions(log_if=True):
    """
    A decorator that catches any exceptions thrown by the decorated function and
    logs them along with a traceback that includes every local variable of every
    frame.

    Notes:
      Caught exceptions are re-raised.

    Args:

      log_if (bool): a flag that can disable logging. This argument can be used
                     to disable/enable logging in specific situations. For
                     example, it can be set to the result of:

                     os.getenv('MYAPP_DEBUG') is not None

                     to make sure logging is only performed when the MYAPP_DEBUG
                     environment variable is defined.

    Returns:
      A decorator that catches and logs exceptions thrown by decorated functions.

    Raises:
      Nothing. The decorator will re-raise any exception caught by the decorated
      function.
    """

    def decorator(func):
        def wrapper(*args, **kwds):
            # this variable is never used. it exists so we can detect if a frame is
            # referencing this specific function.
            __lgw_marker_local__ = 0

            try:
                return func(*args, **kwds)
            except Exception as e:
                if not log_if:
                    raise

                try:
                    # log exception information first in case something fails below
                    print('Exception thrown, %s: %s\n' % (type(e), str(e)))

                    # iterate through the frames in reverse order so we print the
                    # most recent frame first
                    frames = inspect.getinnerframes(sys.exc_info()[2])
                    for frame_info in reversed(frames):
                        f_locals = frame_info[0].f_locals

                        # if there's a local variable named __lgw_marker_local__, we assume
                        # the frame is from a call of this function, 'wrapper', and we skip
                        # it. Printing these frames won't help determine the cause of an
                        # exception, so skipping it reduces clutter.
                        if '__lgw_marker_local__' in f_locals:
                            continue

                        # log the frame information
                        print(LOG_FRAME_TPL %
                                       (frame_info[1], frame_info[2], frame_info[3], frame_info[4][0].lstrip()))

                        # log every local variable of the frame
                        for k, v in f_locals.items():
                            print('    %s = %s\n' % (k, v))
                except Exception as e:
                    print (e)

                print('\n')

                raise

        return wrapper

    return decorator