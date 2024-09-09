from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: int
    __name__: str

    # Автоматическое создание имени таблицы на основе имени класса
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
