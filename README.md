# praktikum_new_diplom
# Логин: admin,
# Пароль: 1234554321,
# email: 123@mail.ru, 
# Адрес сервера: http://158.160.23.86/

-

# Проект **foodgram-project-react** 

Foodgram, «Продуктовый помощник» - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 



# Запуск проекта через docker-compose на удалённом сервере:
Должен быть уставлен Docker https://www.docker.com

Клонируем репозиторий и переходим в него:

```
git clone git@github.com:Dmitriy8854/foodgram-project-react.git

```
cd foodgram-project-react

```
cd foodgram-project-react

```
Установите на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose

```
Скопируйте на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):
```
scp docker-compose.yml nginx.conf <username>@<IP>:/home/<username>/   # username - имя пользователя на сервере
                                                                      # IP - публичный IP сервера
```
Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```

SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```
Создать и запустить контейнеры Docker (выполните команды на сервере)
```
sudo docker-compose up -d
```
После успешной сборки выполнить миграции:
```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
Соберите статику:
```
sudo docker-compose exec backend python manage.py collectstatic --no-input

```
Заполните базу ингредиентами:
```
sudo docker-compose exec backend python manage.py loadingredients

```

### **Автор:**
- [Морозов Дмитрий]
