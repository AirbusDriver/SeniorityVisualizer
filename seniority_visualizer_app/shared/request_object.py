import typing as t


class UseCaseRequest:
    @property
    def errors(self) -> t.List[t.Dict[str, str]]:
        if not hasattr(self, "_errors"):
            self._errors: t.List[t.Dict[str, str]] = []
            return self._errors
        else:
            return self._errors

    @errors.setter
    def errors(self, val):
        raise AttributeError("errors can not be assigned. Use 'add_error' instead")

    def add_error(self, parameter, message):
        self.errors.append({"parameter": parameter, "message": message})

    def has_errors(self):
        return len(self.errors) > 0


class InvalidRequestObject(UseCaseRequest):
    def __nonzero__(self):
        return False

    __bool__ = __nonzero__


class ValidRequestObject(object):
    @classmethod
    def from_dict(cls, adict):
        raise NotImplementedError

    def __nonzero__(self):
        return True

    __bool__ = __nonzero__
