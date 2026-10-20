# ---------- build stage ----------
FROM maven:3.9-eclipse-temurin-17-alpine AS build

WORKDIR /build

COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn clean package -DskipTests

# ---------- runtime stage ----------
FROM eclipse-temurin:17-jre-alpine

# Удаляем ненужные пакеты и обновляем оставшиеся
RUN apk update && apk upgrade --no-cache \
    && apk del --no-cache \
        coreutils \
        gnupg \
        freetype \
    && addgroup -S appuser \
    && adduser -S -u 10001 -G appuser appuser \
    && mkdir -p /app \
    && chown -R appuser:appuser /app \
    && chmod 750 /app \
    && rm -rf /var/cache/apk/* /tmp/*

WORKDIR /app

COPY --from=build /build/target/spring-petclinic-*.jar /app/petclinic.jar

RUN chown appuser:appuser /app/petclinic.jar

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD wget -qO- http://localhost:8080/actuator/health | grep -q '"status":"UP"' || exit 1

USER appuser

ENTRYPOINT ["java", "-jar", "petclinic.jar"]