class SeniorityListError(Exception):
    """SeniorityList operation error"""

    pass


class CalculationError(Exception):
    """Error occured performing caclulation"""

    pass


class LoaderError(Exception):
    """Error occurred during loader operation"""

    pass


class DatasourceValidationError(LoaderError):
    """Datasource has improper data"""

    pass


class DatasourceSchemaError(DatasourceValidationError):
    """Datasource has schema problem"""

    pass


class RepositoryError(Exception):
    """Error in Repository Layer"""

    pass


class UseCaseError(Exception):
    """Error processing UseCase"""

    def __init__(self, error=None, use_case=None):
        self.use_case = use_case
        self.original_error: Exception = error

        super().__init__(self.make_message())

    def make_message(self) -> str:
        if self.use_case is not None and self.original_error is not None:
            s = f"{type(self.use_case).__name__} raised -> {type(self.original_error)}: {self.original_error}"
            return s

        return "UseCase error occurred"
