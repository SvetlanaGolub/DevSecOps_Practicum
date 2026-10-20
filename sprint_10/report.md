# Spring PetClinic — DevSecOps
  
**Автор:** Svetlana Golub      
**Дата начала расследования:** 09.09.2026   

Проект по обеспечению безопасности Spring PetClinic на этапах разработки, CI/CD и Kubernetes.

## Структура проекта

sprint10/  
├── README.md - Описание проекта, структуры и результатов проверок  
├── SECURITY_DESIGN.md - Архитектура и модель угроз STRIDE  
├── Dockerfile - Multi-stage сборка приложения, запуск от non-root    
├── docker-compose.yml - Локальный запуск PetClinic + PostgreSQL  
├── .gitlab-ci.yml - CI/CD и автоматические проверки безопасности  
│  
├── artifacts/  
|   ├── cicd_reports/ - Отчёты, полученные в процессе выполнения пайплайна  
│   └── PetClinic.drawio - Схема развёртывания  
│    
├── k8s/ - Kubernetes-манифесты    
│   ├── deployment.yaml - Развёртывание приложения PetClinic    
│   ├── postgres-statefulset.yaml - Развёртывание PostgreSQL с постоянным хранилищем    
│   ├── postgres-service.yaml - Сервис для доступа к PostgreSQL    
│   ├── service.yaml - Kubernetes Service для PetClinic    
│   ├── ingress.yaml - Ingress для внешнего доступа к PetClinic    
│   ├── networkpolicy.yaml - Сетевые политики Kubernetes: default deny и разрешение необходимых соединений    
│   ├── falco-rules.yaml - Пользовательское правило Falco для обнаружения записи вне /tmp    
│   ├── kyverno-policy.yaml - Политика Kyverno для контроля securityContext Pod'ов    
│   ├── zap-job.yaml - Kubernetes Job для OWASP ZAP baseline scan  
│   └── kube-bench-job.yaml - Kubernetes Job для проверки CIS Benchmark  
│  
└── reports/ - Результаты локальных и Kubernetes-проверок + логи Falco и Kyverno  
    ├── falco-log.md - Доказательство работы правила Falco  
    ├── kyverno-log.md - Доказательство работы правила Kyverno   
    ├── sonarqube.json - Результаты статического анализа SonarQube  
    ├── gitleaks.json - Результаты поиска секретов Gitleaks   
    ├── hadolint.json - Результаты проверки Dockerfile Hadolint  
    ├── trivy.json - Результаты сканирования уязвимостей Trivy  
    ├── dockle.json - Результаты аудита Docker-образа Dockle  
    ├── zap.json - JSON-отчёт OWASP ZAP  
    └── kube-bench.txt - Результаты проверки Kubernetes по CIS Benchmark  


## Security

Основные реализованные меры:

- запуск контейнеров от непривилегированных пользователей;
- `readOnlyRootFilesystem`;
- `allowPrivilegeEscalation: false`;
- `capabilities.drop: ALL`;
- Kubernetes Secrets для чувствительных данных;
- использование образа из Harbor по digest;
- Kubernetes NetworkPolicy с default deny;
- Falco для runtime-мониторинга;
- Kyverno для admission-контроля;
- OWASP ZAP для динамического анализа;
- kube-bench для аудита Kubernetes по CIS Benchmark.

## Результаты проверок

Результаты локальных и Kubernetes-проверок находятся в каталоге [`reports/`](reports/).

Так же в каталоге находятся доказательства-логи работы правил Falco и Kyverno.

### SonarQube

Полный результат:
**[SonarQube — ссылка на сканирование](https://sonarqube.devsecops.education-services.ru/dashboard?id=final_project_s24130742)**

### ZAP

Baseline scan PetClinic:

- 58 PASS
- 3 WARN
- 0 FAIL

- [`zap.json`](reports/zap.json)

### kube-bench

Полный результат CIS Kubernetes Benchmark:

- [`kube-bench.txt`](reports/kube-bench.txt)

## CI/CD

Зелёный pipeline:

**[GitLab CI — ссылка на pipeline](https://devsecops.gitlab.yandexcloud.net/s24130742/sprint_10/-/pipelines/14474)**

В pipeline выполняются проверки безопасности проекта, сборка образа и его публикация в Harbor.

Статическое SCA-сканирование реализовано с помощью trivy ещё до сборки образа. Сам образ проходит сканирование в Harbor

[Отчёты, полученные в процессе выполнения пайплайна](artifacts/cicd_reports/) 

## Container Registry

Образ приложения:

**[Harbor — ссылка на образ](https://harbor.devsecops.education-services.ru/harbor/projects/98/repositories/spring-petclinic/artifacts-tab/artifacts/sha256:2977b4d2b2cfcd38a73077549c179e18ead6846f9cf85de040bee4e90ee02d4d?sbomDigest=)**

Образ используется в Kubernetes по immutable digest.

## Архитектура

Схема развёртывания:

[`PetClinic.drawio`](artifacts/PetClinic.drawio)

Описание архитектуры и модель угроз:

[`SECURITY_DESIGN.md`](SECURITY_DESIGN.md)

## .env 

Чувствительные данные, такие как файл .env, необходимо добавлять в .gitignore, чтобы они не попадали в репозиторий. Если секрет уже был закоммичен, считаем его скомпрометированным и необходимо немедленно ротировать секрет и обновить везде, где необходимо.  
  
<br>

---
<br>
<br>


# Spring PetClinic Sample Application [![Build Status](https://github.com/spring-projects/spring-petclinic/actions/workflows/maven-build.yml/badge.svg)](https://github.com/spring-projects/spring-petclinic/actions/workflows/maven-build.yml)[![Build Status](https://github.com/spring-projects/spring-petclinic/actions/workflows/gradle-build.yml/badge.svg)](https://github.com/spring-projects/spring-petclinic/actions/workflows/gradle-build.yml)

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/spring-projects/spring-petclinic) [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=7517918)

## Understanding the Spring Petclinic application with a few diagrams

See the presentation here:  
[Spring Petclinic Sample Application (legacy slides)](https://speakerdeck.com/michaelisvy/spring-petclinic-sample-application?slide=20)

> **Note:** These slides refer to a legacy, pre–Spring Boot version of Petclinic and may not reflect the current Spring Boot–based implementation.  
> For up-to-date information, please refer to this repository and its documentation.


## Run Petclinic locally

Spring Petclinic is a [Spring Boot](https://spring.io/guides/gs/spring-boot) application built using [Maven](https://spring.io/guides/gs/maven/) or [Gradle](https://spring.io/guides/gs/gradle/).
Java 17 or later is required for the build, and the application can run with Java 17 or newer.

You first need to clone the project locally:

```bash
git clone https://github.com/spring-projects/spring-petclinic.git
cd spring-petclinic
```
If you are using Maven, you can start the application on the command-line as follows:

```bash
./mvnw spring-boot:run
```
With Gradle, the command is as follows:

```bash
./gradlew bootRun
```

You can then access the Petclinic at <http://localhost:8080/>.

<img width="1042" alt="petclinic-screenshot" src="https://cloud.githubusercontent.com/assets/838318/19727082/2aee6d6c-9b8e-11e6-81fe-e889a5ddfded.png">

You can, of course, run Petclinic in your favorite IDE.
See below for more details.

## Building a Container

There is no `Dockerfile` in this project. You can build a container image (if you have a docker daemon) using the Spring Boot build plugin:

```bash
./mvnw spring-boot:build-image
```

## Running the Container Image

```bash
docker images | grep petclinic
docker run -p 8080:8080 docker.io/library/spring-petclinic:latest
```

## In case you find a bug/suggested improvement for Spring Petclinic

Our issue tracker is available [here](https://github.com/spring-projects/spring-petclinic/issues).

## Database configuration

In its default configuration, Petclinic uses an in-memory database (H2) which
gets populated at startup with data. The h2 console is exposed at `http://localhost:8080/h2-console`,
and it is possible to inspect the content of the database using the `jdbc:h2:mem:<uuid>` URL. The UUID is printed at startup to the console.

A similar setup is provided for MySQL and PostgreSQL if a persistent database configuration is needed. Note that whenever the database type changes, the app needs to run with a different profile: `spring.profiles.active=mysql` for MySQL or `spring.profiles.active=postgres` for PostgreSQL. See the [Spring Boot documentation](https://docs.spring.io/spring-boot/how-to/properties-and-configuration.html#howto.properties-and-configuration.set-active-spring-profiles) for more detail on how to set the active profile.

You can start MySQL or PostgreSQL locally with whatever installer works for your OS or use docker:

```bash
docker run -e MYSQL_USER=petclinic -e MYSQL_PASSWORD=petclinic -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=petclinic -p 3306:3306 mysql:9.7
```

or

```bash
docker run -e POSTGRES_USER=petclinic -e POSTGRES_PASSWORD=petclinic -e POSTGRES_DB=petclinic -p 5432:5432 postgres:18.4
```

Further documentation is provided for [MySQL](https://github.com/spring-projects/spring-petclinic/blob/main/src/main/resources/db/mysql/petclinic_db_setup_mysql.txt)
and [PostgreSQL](https://github.com/spring-projects/spring-petclinic/blob/main/src/main/resources/db/postgres/petclinic_db_setup_postgres.txt).

Instead of vanilla `docker` you can also use the provided `docker-compose.yml` file to start the database containers. Each one has a service named after the Spring profile:

```bash
docker compose up mysql
```

or

```bash
docker compose up postgres
```

## Test Applications

At development time we recommend you use the test applications set up as `main()` methods in `PetClinicIntegrationTests` (using the default H2 database and also adding Spring Boot Devtools), `MySqlTestApplication` and `PostgresIntegrationTests`. These are set up so that you can run the apps in your IDE to get fast feedback and also run the same classes as integration tests against the respective database. The MySql integration tests use Testcontainers to start the database in a Docker container, and the Postgres tests use Docker Compose to do the same thing.

## Compiling the CSS

There is a `petclinic.css` in `src/main/resources/static/resources/css`. It was generated from the `petclinic.scss` source, combined with the [Bootstrap](https://getbootstrap.com/) library. If you make changes to the `scss`, or upgrade Bootstrap, you will need to re-compile the CSS resources using the Maven profile "css", i.e. `./mvnw package -P css`. There is no build profile for Gradle to compile the CSS.

## Working with Petclinic in your IDE

### Prerequisites

The following items should be installed in your system:

- Java 17 or newer (full JDK, not a JRE)
- [Git command line tool](https://help.github.com/articles/set-up-git)
- Your preferred IDE
  - Eclipse with the m2e plugin. Note: when m2e is available, there is a m2 icon in `Help -> About` dialog. If m2e is
  not there, follow the installation process [here](https://www.eclipse.org/m2e/)
  - [Spring Tools Suite](https://spring.io/tools) (STS)
  - [IntelliJ IDEA](https://www.jetbrains.com/idea/)
  - [VS Code](https://code.visualstudio.com)

### Steps

1. On the command line run:

    ```bash
    git clone https://github.com/spring-projects/spring-petclinic.git
    ```

1. Inside Eclipse or STS:

    Open the project via `File -> Import -> Maven -> Existing Maven project`, then select the root directory of the cloned repo.

    Then either build on the command line `./mvnw generate-resources` or use the Eclipse launcher (right-click on project and `Run As -> Maven install`) to generate the CSS. Run the application's main method by right-clicking on it and choosing `Run As -> Java Application`.

1. Inside IntelliJ IDEA:

    In the main menu, choose `File -> Open` and select the Petclinic [pom.xml](pom.xml). Click on the `Open` button.

    - CSS files are generated from the Maven build. You can build them on the command line `./mvnw generate-resources` or right-click on the `spring-petclinic` project then `Maven -> Generates sources and Update Folders`.

    - A run configuration named `PetClinicApplication` should have been created for you if you're using a recent Ultimate version. Otherwise, run the application by right-clicking on the `PetClinicApplication` main class and choosing `Run 'PetClinicApplication'`.

1. Navigate to the Petclinic

    Visit [http://localhost:8080](http://localhost:8080) in your browser.

## Looking for something in particular?

|Spring Boot Configuration | Class or Java property files  |
|--------------------------|---|
|The Main Class | [PetClinicApplication](https://github.com/spring-projects/spring-petclinic/blob/main/src/main/java/org/springframework/samples/petclinic/PetClinicApplication.java) |
|Properties Files | [application.properties](https://github.com/spring-projects/spring-petclinic/blob/main/src/main/resources) |
|Caching | [CacheConfiguration](https://github.com/spring-projects/spring-petclinic/blob/main/src/main/java/org/springframework/samples/petclinic/system/CacheConfiguration.java) |

## Interesting Spring Petclinic branches and forks

The Spring Petclinic "main" branch in the [spring-projects](https://github.com/spring-projects/spring-petclinic)
GitHub org is the "canonical" implementation based on Spring Boot and Thymeleaf. There are
[quite a few forks](https://spring-petclinic.github.io/docs/forks.html) in the GitHub org
[spring-petclinic](https://github.com/spring-petclinic). If you are interested in using a different technology stack to implement the Pet Clinic, please join the community there.

## Interaction with other open-source projects

One of the best parts about working on the Spring Petclinic application is that we have the opportunity to work in direct contact with many Open Source projects. We found bugs/suggested improvements on various topics such as Spring, Spring Data, Bean Validation and even Eclipse! In many cases, they've been fixed/implemented in just a few days.
Here is a list of them:

| Name | Issue |
|------|-------|
| Spring JDBC: simplify usage of NamedParameterJdbcTemplate | [SPR-10256](https://github.com/spring-projects/spring-framework/issues/14889) and [SPR-10257](https://github.com/spring-projects/spring-framework/issues/14890) |
| Bean Validation / Hibernate Validator: simplify Maven dependencies and backward compatibility |[HV-790](https://hibernate.atlassian.net/browse/HV-790) and [HV-792](https://hibernate.atlassian.net/browse/HV-792) |
| Spring Data: provide more flexibility when working with JPQL queries | [DATAJPA-292](https://github.com/spring-projects/spring-data-jpa/issues/704) |

## Contributing

The [issue tracker](https://github.com/spring-projects/spring-petclinic/issues) is the preferred channel for bug reports, feature requests and submitting pull requests.

For pull requests, editor preferences are available in the [editor config](.editorconfig) for easy use in common text editors. Read more and download plugins at <https://editorconfig.org>. All commits must include a __Signed-off-by__ trailer at the end of each commit message to indicate that the contributor agrees to the Developer Certificate of Origin.
For additional details, please refer to the blog post [Hello DCO, Goodbye CLA: Simplifying Contributions to Spring](https://spring.io/blog/2025/01/06/hello-dco-goodbye-cla-simplifying-contributions-to-spring).

## License

The Spring PetClinic sample application is released under version 2.0 of the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).
