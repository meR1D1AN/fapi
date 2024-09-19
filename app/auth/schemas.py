from pydantic import BaseModel, EmailStr, validator
import re


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    password_confirm: str

    @validator('phone')
    def phone_must_match_pattern(cls, v):
        """
        Валидатор номера телефона.
        Проверяет, соответствует ли номер телефона шаблону "+7ХХХХХХХХХХ", где Х - цифра.
        Аргументы:
            v (str): Номер телефона.
        Возвращает:
            str: Номер телефона, если он соответствует шаблону.
        Выбрасывает:
            ValueError: Если номер телефона не соответствует шаблону.
        """
        pattern = re.compile(r'^\+7\d{10}$')
        if not pattern.match(v):
            raise ValueError('Номер телефона должен начинаться с +7 и содержать 10 цифр')
        return v

    @validator('password')
    def validate_password(cls, v):
        """
        Валидатор пароля.
        Проверяет, соответствует ли пароль следующим требованиям:
        - Длина пароля не менее 8 символов.
        - Пароль содержит хотя бы одну заглавную букву.
        - Пароль содержит хотя бы один специальный символ ($%&!:).
        Аргументы:
            v (str): Пароль.
        Возвращает:
            str: Пароль, если он соответствует требованиям.
        Выбрасывает:
            ValueError: Если пароль не соответствует требованиям.
        """
        if len(v) < 8 or not any(c.isupper() for c in v) or not any(c in '$%&!:' for c in v):
            raise ValueError(
                'Пароль должен содержать не менее 8 символов, одну заглавную букву и один специальный символ ($%&!:).')
        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """
        Валидатор подтверждения пароля.
        Проверяет, совпадает ли подтвержденный пароль с основным паролем.
        Аргументы:
            v (str): Подтвержденный пароль.
            values (dict): Словарь значений, содержащий основной пароль.
        Возвращает:
            str: Подтвержденный пароль, если он совпадает с основным паролем.
        Выбрасывает:
            ValueError: Если подтвержденный пароль не совпадает с основным паролем.
        """
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "full_name": "Полное Ф.И.О.",
                "email": "user@example.com",
                "phone": "+79999999999",
                "password": "passworD123!",
                "password_confirm": "passworD123!"
            }
        }


class UserRegister(UserCreate):
    class Config:
        from_attributes = True


class UserOut(UserCreate):
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True
