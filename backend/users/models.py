from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    '''
    Модель пользователя на основе импортируемой абстрактной модели.
    '''
    pass
