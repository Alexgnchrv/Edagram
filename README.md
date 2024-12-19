# Foodgram 🍽️

**Foodgram** — это платформа для обмена рецептами, создания списков покупок и подписки на авторов. Пользователи могут публиковать свои рецепты, добавлять понравившиеся в «Избранное», подписываться на других авторов и создавать список продуктов для покупок.

## Основные функции:
- **Публикация рецептов** с описанием и фотографиями.
- **Избранное** для сохранения понравившихся рецептов.
- **Подписка на авторов** для получения обновлений.
- **Список покупок** для удобного планирования покупок по выбранным рецептам.
- **Генерация сводного списка продуктов** для нескольких рецептов в формате .txt.
- **Тэги** для удобной навигации по рецептам.

## Установка и запуск

1. Клонируйте репозиторий на свой локальный компьютер:
    ```bash
    git clone git@github.com:yourusername/foodgram.git
    cd foodgram
    ```

2. Создайте файл `.env` и заполните его своими данными, используя образец `.env.example`, который находится в корневой директории проекта.

## Создание и загрузка Docker-образов

1. Построение Docker-образов:
    ```bash
    cd frontend
    docker build -t username/foodgram_frontend .

    cd ../backend
    docker build -t username/foodgram_backend .

    cd ../nginx
    docker build -t username/foodgram_gateway .
    ```

2. Загрузка образов в DockerHub:
    ```bash
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```

## Деплой на сервер

1. Подключитесь к удаленному серверу:
    ```bash
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
    ```

2. Создайте директорию проекта на сервере:
    ```bash
    mkdir foodgram
    ```

3. Скопируйте файл `docker-compose.production.yml` из базовой папки на сервер:
    ```bash
    scp -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом ./docker-compose.production.yml имя_пользователя@ip_адрес_сервера:/home/имя_пользователя/foodgram/
    ```

4. Скопируйте файл `nginx.conf` из папки `infra` на сервер:
    ```bash
    scp -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом ./infra/nginx.conf имя_пользователя@ip_адрес_сервера:/home/имя_пользователя/foodgram/infra/
    ```

5. Скопируйте файлы из папки `docs` в аналогичную папку на сервере:
    ```bash
    scp -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом ./docs/* имя_пользователя@ip_адрес_сервера:/home/имя_пользователя/foodgram/docs/
    ```

6. Установите Docker и Docker Compose на сервер:
    ```bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt install docker-compose-plugin 
    ```

7. Запустите Docker Compose в режиме демона:
    ```bash
    sudo docker compose -f docker-compose.production.yml up -d
    ```

8. Выполните миграции и соберите статические файлы:
    ```bash
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/static/. /staticfiles/
    ```

## Настройка Nginx

1. Редактируйте конфигурацию Nginx:
    ```bash
    sudo nano /etc/nginx/sites-enabled/default
    ```

2. Обновите настройки `location`:
    ```nginx
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
    ```

3. Проверьте конфигурацию Nginx:
    ```bash
    sudo nginx -t
    ```

4. Если ошибок нет, перезапустите Nginx:
    ```bash
    sudo service nginx reload
    ```

## Настройка CI/CD

1. Файл workflow находится в директории `.github/workflows/main.yml`. Он автоматизирует процесс тестирования и деплоя на сервер.

2. Для настройки GitHub Actions добавьте следующие секреты в настройки репозитория на GitHub:
    - **DOCKER_USERNAME** — логин DockerHub
    - **DOCKER_PASSWORD** — пароль DockerHub
    - **HOST** — IP-адрес сервера
    - **USER** — имя пользователя на сервере
    - **SSH_KEY** — приватный SSH-ключ (получите с помощью `cat ~/.ssh/id_rsa`)
    - **SSH_PASSPHRASE** — пароль для SSH-ключа
    - **TELEGRAM_TO** — ID вашего Telegram-аккаунта (узнайте у `@userinfobot`)
    - **TELEGRAM_TOKEN** — токен вашего Telegram-бота (создайте через `@BotFather`)

## Проверка перед отправкой

1. Убедитесь, что Foodgram доступен по указанному доменному имени.
2. Пуш в ветку `main` запускает автоматическое тестирование и деплой.
3. После успешного деплоя приходит уведомление в Telegram.
4. Все контейнеры успешно работают на сервере.
