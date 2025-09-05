import src.globals as g
import supervisely as sly
from supervisely.io.exception_handlers import ErrorHandler


def handle_exception_and_stop(exc: Exception, msg: str = "Error"):
    from supervisely.io.exception_handlers import (
        handle_exception as sly_handle_exception,
    )

    sly.fs.clean_dir(g.app_data)

    debug_info = {
        "team_id": g.team_id,
        "workspace_id": g.workspace_id,
        "project_id": g.project_id,
        "dataset_id": g.dataset.id if g.dataset is not None else None,
    }

    handled_exc = sly_handle_exception(exc)
    if handled_exc is not None:
        err_msg = handled_exc.get_message_for_exception()
        sly.logger.error(err_msg, extra=debug_info, exc_info=True)
        if isinstance(handled_exc, ErrorHandler.API.PaymentRequired):
            raise exc
        else:
            g.api.task.set_output_error(g.task_id, handled_exc.title, handled_exc.message)
    else:
        err_msg = repr(exc)
        if len(err_msg) > 255:
            err_msg = err_msg[:252] + "..."
        g.api.task.set_output_error(g.task_id, msg, err_msg)
        exc_str = str(exc) if isinstance(exc, RuntimeError) else repr(exc)  # for better logging
        sly.logger.error(f"{msg}. {exc_str}", extra=debug_info, exc_info=True)
    exit(0)
