from pydantic import BaseModel, EmailStr, validator


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    password_confirm: str

    @validator('phone')
    def phone_must_match_pattern(cls, v):
        import re
        pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')  # Замените на желаемый рисунок
        if not pattern.match(v):
            raise ValueError('Неверный номер телефона')
        return v

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 8 or not any(c.isupper() for c in value) or not any(c in '$%&!:' for c in value):
            raise ValueError(
                'Пароль должен содержать не менее 8 символов, одну заглавную букву и один специальный символ ($%&!:).')
        return value

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v
