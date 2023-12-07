import logging
import sys
import traceback

logger = logging.getLogger("uvicorn.default")


def log_exception():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    tb = traceback.extract_tb(ex_traceback)
    stack_top = tb[0]
    stack_bottom = tb[-1]
    logger.warning(
        f'Exception {ex_type.__name__}("{ex_value}") caught. Stack: '
        f"[{stack_top[0]} / L:{stack_top[1]} / {stack_top[2]} / {stack_top[3]}] "
        f"--> [{stack_bottom[0]} / L:{stack_bottom[1]} / "
        f"{stack_bottom[2]} / {stack_bottom[3]}]"
    )
