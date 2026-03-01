class DomainException(Exception):

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SuratNotFoundException(DomainException):

    def __init__(self, message: str = "Surat tidak ditemukan"):
        super().__init__(message, 404)


class UserNotFoundException(DomainException):

    def __init__(self, message: str = "User tidak ditemukan"):
        super().__init__(message, 404)


class InvalidStatusTransitionError(DomainException):

    def __init__(self, message: str = "Transisi status tidak valid"):
        super().__init__(message, 400)


class InvalidCredentialsError(DomainException):

    def __init__(self, message: str = "Kredensial tidak valid"):
        super().__init__(message, 401)


class InvalidDocumentError(DomainException):

    def __init__(self, message: str = "Dokumen tidak valid"):
        super().__init__(message, 400)


class InvalidUserIdentityError(DomainException):

    def __init__(self, message: str = "Identitas user tidak valid"):
        super().__init__(message, 400)


class DuplicateEmailError(DomainException):

    def __init__(self, message: str = "Email sudah terdaftar"):
        super().__init__(message, 409)
