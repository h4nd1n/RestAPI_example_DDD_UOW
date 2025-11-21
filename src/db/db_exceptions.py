from sqlalchemy.exc import IntegrityError


class QADatabaseBaseException(Exception):
    pass


class UniqueConstraintViolation(QADatabaseBaseException):
    detail = "Unique constraint violated"


class ForeignKeyViolation(QADatabaseBaseException):
    detail = "Foreign key constraint violated"


def map_integrity_error(e: IntegrityError):
    orig = e.orig
    name = orig.__class__.__name__.lower()
    msg = str(orig).lower()

    # 1) по имени исключения (универсально для asyncpg и psycopg)
    if "unique" in name:
        return UniqueConstraintViolation()
    if "foreign" in name or "referential" in name:
        return ForeignKeyViolation()

    # 2) fallback по тексту сообщения — работает всегда
    if "unique" in msg:
        return UniqueConstraintViolation()
    if "foreign key" in msg or "violates foreign key" in msg:
        return ForeignKeyViolation()

    # неизвестная ошибка целостности
    return e
