from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Автоматическое создание имени таблицы на основе имени класса.
        Возвращает:
            str: Имя таблицы, созданное на основе имени класса.
        """
        return cls.__name__.lower()
