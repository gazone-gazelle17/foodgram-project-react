# **Foodgram**
## **Описание**
___

Настоящий проект представляет собой полноценный сайт для создания, просмотра, редактирования, удаления рецептов, добавления их в избранное, подписок на авторов, формирования списка покупок и его скачивания в формате pdf.

## **Технологии**
___
+ *Python 3.9* 
+ *Django Rest Framework* 
+ *Djoser*
+ *SimpleJWT*
+ *dataclasses*
+ *Docker*
+ *docker-compose*
+ *nginx*

## **Запуск проекта**
___

1. Склонируйте репозиторий:
```
git@github.com:gazone-gazelle17/foodgram-project-react.git
```
2. Наполните файл .env, указав переменные:
+ POSTGRES_DB
+ POSTGRES_USER
+ POSTGRES_PASSWORD
+ DB_HOST
+ DB_PORT
+ SECRET_KEY
3. В директории ../infra/ запустите проект командой:
```
sudo docker-compose up
```
4. Выполните миграции и создайте суперпользователя или воспользуйтесь данными ниже.

## **Тестовые данные**
Адрес сервера: http://foodgram-reviewer.chickenkiller.com
Логин администратора: admin@example.com
Пароль администратора: adminpassword

## **Автор**
___

Саша Гасымов
