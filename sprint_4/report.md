# Отчёт по харденингу приложения Spring PetClinic

**Автор:** Svetlana Golub  
**Дата аудита:** 02.07.2026  
**Целевое приложение:** Spring PetClinic, Java

---

Spring PetClinic - веб-приложение на Spring Framework,  работает с базами данных, REST API и MVC-контроллерами.

Технический стек:
- Java 17
- Spring Boot 3.x
- Thymeleaf 
- MySQL
- Maven
- Bootstrap 

## Сборка образа и запуск через docker-compose
```bash
git clone https://github.com/spring-projects/spring-petclinic.git

cd spring-petclinic

docker-compose up -d
```
## Утилиты для сканирования

| Инструмент | Назначение |
|---|---|
| Hadolint | Линтер Dockerfile |
| Dockle | Проверка безопасности образа |
| Trivy | Сканирование контейнера на уязвимости |
| Grype | Сканирование контейнера на уязвимости |
| Docker Bench Security | Проверка соответствия CIS benchmarks |

## Основные исправления
### Hadolint
1. Необходимо добавить версии загружаемых пакетов -> нет необходимости загружать пакеты  

### Dockle
1. Рекомендация добавить DOCKER_CONTENT_TRUST=1 -> использование цифровой подписи контейнеров, технология устаревает и скоро не будет поддерживаться

### Trivy
1. 15 уязвимостей в 3 компонентах - в этих пакетах нет необходимости, удалены

### Grype
1. 36 уязвимостей разного уровня критичности -> некоторые пакеты удалены, большая часть обновлена, 4 остались, так как эти пакеты в выбранном образе обновить до последней версии невозможно, также риск уязвимостей низкий 

### Docker Bench Security
1. Пункты 1.1.3–1.1.18 связаны с отсутствием аудита -> включен auditd и настроены правила аудита для бинарников и директорий Docker, containerd и runc
2. Пункт 2.2 сетевой трафик между контейнерами на bridge не ограничен -> Создана пользовательская сеть petclinic-network вместо использования дефолтного bridge
3. Пункт 2.9 user namespace support отключен → Включен в конфигурации Docker daemon
4. Пункт 2.12 авторизация для клиентских команд Docker не включена -> Добавлен плагин авторизации или использование docker trust
5. Пункт 2.13 централизованное логирование не настроено -> Настроен драйвер логирования syslog или json-file с ротацией
6. Пункт 2.16 Userland Proxy включен -> Отключен в /etc/docker/daemon.json: "userland-proxy": false
7. Пункт 4.1 запуск контейнера от root -> создан непривилегированный пользователь appuser (UID 10001) и добавлена директива USER appuser в Dockerfile
8. Пункты 4.6 и 5.27 отсутствие HEALTHCHECK -> добавлена в Dockerfile через wget проверка /actuator/health, настроены интервал 30s, таймаут 5s, start-period 60s
9. Пункт 4.5 Content Trust для Docker не включен -> Включен через export DOCKER_CONTENT_TRUST=1
10. Пункт 5.3 отсутствие SELinux опций -> Добавлены security_opt: label=type:container_t в docker-compose.yml
11. Пункт 5.9 открыты неиспользуемые порты -> Оставлен только порт 8080 для PetClinic и 3306 для MySQL
12. Пункт 5.11-12, 29 отсутствие ограничений по памяти, процессам и CPU -> добавлены параметр mem_limit, mem_reservation, pids_limit и cpus
13. Пункт 5.13 root FS доступна для записи -> добавлен read_only: true для PetClinic (MySQL оставлен R/W для записи данных в /var/lib/mysql)
14. Пункт 5.14 порты привязаны к 0.0.0.0 (ко всем интерфейсам) -> указана привязка к 127.0.0.1
15. Пункт 5.26 контейнер может получать новые привилегии -> добавлен параметр security_opt: no-new-privileges:true

## Артефакты харденинга

`/reports`  
├──`/after` - отчёты сканирований до харденинга   
│   ├── `bench-security_report.txt`  
│   ├── `dockle_report.txt`  
│   ├── `grype_report.txt`  
│   ├── `hadolint_report.txt`  
│   └── `trivy_report.txt`  
├──`/before` - отчёты сканирований после харденинга    
│   ├── `bench-security_report.txt`  
│   ├── `dockle_report.txt`  
│   ├── `grype_report.txt`  
│   ├── `hadolint_report.txt`  
│   └── `trivy_report.txt`  
├── `Dockerfile` - финальная версия после всех этапов харденинга        
├── `docker-compose.yml` -  файл декларативного описания набора контейнеров после харденинга  
└── `README.md` -  краткие шаги сборки и запуска приложения, перечисление использованных проверок и исправлений

