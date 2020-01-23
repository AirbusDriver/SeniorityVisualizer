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


class RepositoryError:
    """Error in Repository Layer"""

    pass
