# Проект "Foodgram" - продуктовый помощник

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)


## Описание проекта

Продуктовый помощник - это приложение, на котором пользователи делятся рецептами, 
добавляют рецепты в список избранного и подписываются на публикации других авторов. 
Функция «Список покупок» позволит пользователю создавать список продуктов, 
которые ему нужно купить для приготовления выбранных блюд.


## Запуск проекта в dev-режиме

- Клонируйте репозиторий с проектом на свой компьютер. В терминале из рабочей директории выполните команду:
```bash
git clone git@github.com:PetrushinAlex/foodgram.git
```

- Установить и активировать виртуальное окружение
```bash
source /venv/Scripts/activate
```

- Установить зависимости из файла requirements.txt
```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

- Создать файл .env в папке проекта. В директории проекта лежит файл .env.example. Этот файл является примером, какие переменные описывать.

### Выполните миграции, запустите локально и создайте супер юзера:

- В папке с файлом manage.py (по умолчанию - /foodgram/backend/) выполнить команду:
```bash
python manage.py migrate
```

- Далее запускайте сервер:
```bash
python manage.py runserver
```

- Создайте нового супер юзера: 
```bash
python manage.py createsuperuser
```

### Загрузите статику:

```bash
python manage.py collectstatic --no-input
```

### Заполните базу тестовыми данными:

```bash
python manage.py add_tags_from_data
python manage.py add_ingidients_from_data 
```

## Запуск проекта через Docker

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:
```bash
git clone git@github.com:PetrushinAlex/foodgram.git
```

- в Docker cоздаем образ:

```bash
docker build -t foodgram .
```

Выполните команду:

```bash
cd ../infra
docker-compose up -d --build
```

- В результате должны быть собрано три контейнера, при введении следующей команды получаем список запущенных контейнеров:

```bash
docker-compose ps
```

### Выполните миграции:

```bash
docker-compose exec backend python manage.py migrate
```
### Создайте суперпользователя:

```bash
docker-compose exec backend python manage.py createsuperuser
```

### Загрузите статику:

```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

### Заполните базу тестовыми данными:

```bash
docker-compose exec backend python manage.py add_tags_from_data
docker-compose exec backend python manage.py add_ingidients_from_data   
```

### Основные адреса: 

| Адрес                 | Описание |
|:----------------------|:---------|
| 127.0.0.1            | Главная страница |
| 127.0.0.1/admin/     | Для входа в панель администратора |
| 127.0.0.1/api/docs/  | Описание работы API |

## Фронтенд и спецификация API
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.


### Автор:  
_Петрушин Александр_<br>
**email**: _jacka.92@yandex.ru_<br>
**telegram** _@hello_pachany_
