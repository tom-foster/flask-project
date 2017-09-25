## created so that errors in the api, can return a bad request
## based on the ValueError class.

class ValidationError(ValueError):
    pass