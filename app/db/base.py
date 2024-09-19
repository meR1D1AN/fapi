from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Автоматически генерируемое имя таблицы.
        Оно равно имени класса, но в нижнем регистре.
        """
        return cls.__name__.lower()