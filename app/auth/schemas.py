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
        pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')  # Replace with your desired pattern
        if not pattern.match(v):
            raise ValueError('Invalid phone number')
        return v

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 8 or not any(c.isupper() for c in value) or not any(c in '$%&!:' for c in value):
            raise ValueError(
                'Password must contain at least 8 characters, one uppercase letter, and one special character ($%&!:)')
        return value

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
