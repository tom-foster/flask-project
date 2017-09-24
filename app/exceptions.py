## created so that errors in the api, can return a bad request

class ValidationError(ValueError):
    pass