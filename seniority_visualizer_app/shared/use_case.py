import logging
from pprint import pformat
from seniority_visualizer_app.shared import response_object as res

logger = logging.getLogger(__name__)


class UseCase(object):
    def execute(self, request_object):
        if not request_object:
            logger.debug(f"BAD USECASE REQUEST!")
            logger.debug(f"{type(request_object).__name__} -> {pformat(vars(request_object))}")
            return res.ResponseFailure.build_from_invalid_request_object(request_object)
        try:
            return self.process_request(request_object)
        except Exception as exc:
            resp = res.ResponseFailure.build_system_error(
                "{}: {}".format(exc.__class__.__name__, "{}".format(exc))
            )
            logger.exception(f"{type(self).__name__} -> {resp.message}", exc_info=exc)
            return resp

    def process_request(self, request_object):
        raise NotImplementedError("process_request() not implemented by UseCase class")
