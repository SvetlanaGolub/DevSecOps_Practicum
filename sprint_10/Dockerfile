# ---------- build stage ----------
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /build

# Копируем pom.xml для кеширования зависимостей
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Копируем исходный код
COPY src ./src

# Собираем приложение
RUN mvn clean package -DskipTests -B

# ---------- runtime stage ----------
FROM eclipse-temurin:21-jre

WORKDIR /app

# Обновляем пакеты
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Создаём непривилегированного пользователя
RUN groupadd --system petclinic \
    && useradd --system \
       --gid petclinic \
       --home-dir /app \
       --shell /usr/sbin/nologin \
       petclinic

# Копируем только готовый JAR из build-stage
COPY --from=builder /build/target/*.jar /app/app.jar

RUN chown petclinic:petclinic /app/app.jar

USER petclinic

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]