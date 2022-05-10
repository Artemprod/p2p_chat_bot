## Installation
```bash
    pip install -r requirements.txt
```

## Run
```bash
    TOKEN="TOKEN" BD_PASSWORD="BD_PASSWORD" python bot_v2.py
```

## Docker
### Посмотреть готовый файл docker-compose.yml
```bash
docker-compose -f docker-compose.yml config
```

### Запуск
```bash
docker-compose -f docker-compose.yml up
```

### Сборка
```bash
docker-compose -f docker-compose.yml build server
```
