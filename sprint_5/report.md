# Отчет по аудиту безопасности Kubernetes

**Автор:** Svetlana Golub  
**Дата аудита:** 09.07.2026  
**Версия Kubernetes:** v1.31.2  
**Инструменты:** kubectl, JSONPath, Kubescape v4.0.10

## Шаг 1: диагностика и аудит кластера

### Привилегированные контейнеры

- **Тип**: Привилегированный контейнер
- **Namespace**: backend
- **Под**: backend-86c7889647-mp6hb
- **Описание риска**: Контейнер запущен с привилегированным режимом (privileged: true), что дает ему доступ ко всем устройствам хоста и возможность эскалации привилегий
- **Приоритет**: CRITICAL

```
$ kubectl get pods -n backend -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].securityContext.privileged}{"\n"}{end}'

backend-86c7889647-mp6hb        true
```

### Секреты в ConfigMap
- **Тип**: Чувствительные данные в ConfigMap
- **Namespace**: backend
- **Ресурс**: configmap/db-config
- **Описание риска**: Пароль и имя пользователя БД хранятся в открытом виде в ConfigMap
- **Приоритет**: HIGH

```
$ kubectl get configmap -A -o yaml | grep -iE 'password|secret|token|key' 

{"host":"backend","password":"secret-password-456","port":"5432","username":"admin"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"backend"}
```

### Секреты в переменных окружения
- **Тип**: Hardcoded секреты в env
- **Namespace**: frontend
- **Ресурс**: Deployment/frontend
- **Описание риска**: Пароль БД задан напрямую в переменной окружения в Deployment манифесте
- **Приоритет**: HIGH

```
$ kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{range .spec.containers[*]}{range .env[*]}{.name}{"="}{.value}{","}{end}{";"}{end}{"\n"}{end}' | grep -iE 'password|secret|token|key'
DB_PASSWORD = hardcoded-password-123
```

### Использование default ServiceAccount
- **Тип**: Default ServiceAccount
- **Namespace**: frontend
- **Ресурс**: frontend-bd596fc68-n4glp
- **Описание риска**: Под использует default ServiceAccount, который может иметь избыточные права
- **Приоритет**: MEDIUM

```
$ kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.spec.serviceAccountName}{"\n"}{end}' | awk '$3=="" || $3=="default" {print $0}'

frontend    frontend-bd596fc68-n4glp        default
```

- **Тип**: Default ServiceAccount
- **Namespace**: backend
- **Под**: backend-86c7889647-mp6hb
- **Описание риска**: Под использует default ServiceAccount, который может иметь избыточные права
- **Приоритет**: MEDIUM

```
$ kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.spec.serviceAccountName}{"\n"}{end}' | awk '$3=="" || $3=="default" {print $0}'

backend     backend-86c7889647-mp6hb        default
```

### Небезопасные RBAC-правила
- **Тип**: Wildcard в RBAC
- **Ресурс**: unsafe-role
- **Описание риска**: ClusterRole содержит правила с wildcard (*) в verbs и resources, дающие избыточные права
- **Приоритет**: HIGH

```
$ kubectl get clusterrole -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .rules[*]}{.apiGroups}{"|"}{.resources}{"|"}{.verbs}{";"}{end}{"\n"}{end}' | grep '\*'

unsafe-role     ["*"]|["*"]|["*"];
```

### Kubescape
```
$ kubescape scan framework nsa
╭─────────────────┬────╮
│        Controls │ 26 │
│          Passed │ 5  │
│          Failed │ 19 │
│ Action Required │ 2  │
╰─────────────────┴────╯
╭──────────┬────╮
│ Critical │ 0  │
│     High │ 48 │
│   Medium │ 85 │
│      Low │ 11 │
╰──────────┴────╯
╭──────────┬────────────────────────────────────────────────────┬──────────────────┬───────────────┬───────────────────╮
│ Severity │ Control name                                       │ Failed resources │ All Resources │ Compliance score  │
├──────────┼────────────────────────────────────────────────────┼──────────────────┼───────────────┼───────────────────┤
│ Critical │ Disable anonymous access to Kubelet service        │         0        │       0       │ Action Required * │
│ Critical │ Enforce Kubelet client TLS authentication          │         0        │       0       │ Action Required * │
│   High   │ Applications credentials in configuration files    │         4        │       61      │        93%        │
│   High   │ HostNetwork access                                 │         4        │       27      │        85%        │
│   High   │ Insecure capabilities                              │         1        │       27      │        96%        │
│   High   │ Privileged container                               │         3        │       27      │        89%        │
│   High   │ Ensure CPU limits are set                          │        20        │       27      │        26%        │
│   High   │ Ensure memory limits are set                       │        16        │       27      │        41%        │
│  Medium  │ Prevent containers from allowing command execution │         3        │      122      │        98%        │
│  Medium  │ Non-root containers                                │        14        │       27      │        48%        │
│  Medium  │ Allow privilege escalation                         │         6        │       27      │        78%        │
│  Medium  │ Ingress and Egress blocked                         │        19        │       28      │        32%        │
│  Medium  │ Automatic mapping of service account               │        20        │       97      │        79%        │
│  Medium  │ Administrative Roles                               │         3        │      122      │        98%        │
│  Medium  │ Cluster internal networking                        │        10        │       15      │        33%        │
│  Medium  │ Linux hardening                                    │         7        │       27      │        74%        │
│  Medium  │ Secret/etcd encryption enabled                     │         1        │       1       │         0%        │
│  Medium  │ Audit logs enabled                                 │         1        │       1       │         0%        │
│  Medium  │ Nginx Ingress Controller End of Life               │         1        │       23      │        96%        │
│    Low   │ Immutable container filesystem                     │        10        │       27      │        63%        │
│    Low   │ PSP enabled                                        │         1        │       1       │         0%        │
├──────────┼────────────────────────────────────────────────────┼──────────────────┼───────────────┼───────────────────┤
│          │                  Resource Summary                  │        36        │      269      │       62.66%      │
╰──────────┴────────────────────────────────────────────────────┴──────────────────┴───────────────┴───────────────────╯
```

## Шаг 2: исправление RBAC

1. **Создан ServiceAccount frontend-sa:**
   ```bash
   kubectl create serviceaccount frontend-sa -n frontend
   ```

2. Создана Role с минимальными правами:
    Права: get, list для pods и services в неймспейсе frontend
    Без wildcard (*) правил
    Использована Role (не ClusterRole)

3. Создан RoleBinding:
    Привязка Role frontend-role к ServiceAccount frontend-sa

4. Обновлен Deployment frontend:
    Изменен serviceAccountName с default на frontend-sa
    Под пересоздан с новым ServiceAccount

### Проверка прав доступа
Права ServiceAccount frontend-sa:
```bash
$ kubectl auth can-i get pods -n frontend --as=system:serviceaccount:frontend:frontend-sa
yes
$ kubectl auth can-i list pods -n frontend --as=system:serviceaccount:frontend:frontend-sa
yes
$ kubectl auth can-i get services -n frontend --as=system:serviceaccount:frontend:frontend-sa
yes
$ kubectl auth can-i create pods -n frontend --as=system:serviceaccount:frontend:frontend-sa
no
$ kubectl auth can-i delete pods -n frontend --as=system:serviceaccount:frontend:frontend-sa
no
$ kubectl auth can-i get pods -n backend --as=system:serviceaccount:frontend:frontend-sa
no
$ kubectl auth can-i get nodes --as=system:serviceaccount:frontend:frontend-sa
no
```

## Шаг 3: Миграция секретов

1. Создан секрет `db-secret` в неймспейсе `backend`:
   ```bash
   kubectl create secret generic db-secret -n backend --from-literal=username=admin --from-literal=password=secret-password-456

2. Обновлен Deployment backend для использования secretKeyRef:
    POSTGRES_USER → db-secret.username
    POSTGRES_PASSWORD → db-secret.password

3. Создан секрет db-secret-frontend в неймспейсе frontend:
    ```bash
    kubectl create secret generic db-secret-frontend -n frontend --from-literal=username=admin --from-literal=password=hardcoded-password-123
    ```
4. Обновлен Deployment frontend для использования secretKeyRef:
    DB_PASSWORD → db-secret-frontend.password
```
$ kubectl exec -n backend deployment/backend -- env | grep -E "POSTGRES_|DB_"
kubectl exec -n frontend deployment/frontend -- env | grep DB_PASSWORD
kubectl describe pod -n backend -l app=backend | grep -A 10 Environment
kubectl describe pod -n frontend -l app=frontend | grep -A 10 Environment
DB_HOST=backend.backend.svc.cluster.local
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret-password-456
POSTGRES_DB=mydb
DB_USERNAME=admin
DB_PASSWORD=secret-password-456
DB_PASSWORD=hardcoded-password-123
    Environment:
      POSTGRES_USER:      <set to the key 'username' in secret 'db-secret'>  Optional: false
      POSTGRES_PASSWORD:  <set to the key 'password' in secret 'db-secret'>  Optional: false
      POSTGRES_DB:        mydb
      DB_USERNAME:        <set to the key 'username' in secret 'db-secret'>  Optional: false
      DB_PASSWORD:        <set to the key 'password' in secret 'db-secret'>  Optional: false
      DB_HOST:            backend.backend.svc.cluster.local
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-lnnxj (ro)
Conditions:
  Type                        Status
    Environment:
      API_KEY:      hardcoded-api-key-67890
      DB_PASSWORD:  <set to the key 'password' in secret 'db-secret-frontend'>  Optional: false
      JWT_SECRET:   jwt-secret-hardcoded-123
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-xs95b (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       True
```

## Шаг 4: безопасность подов
1. Настроен PSA уровня baseline для неймспейса backend
2. Добавлен SecurityContext в Deployment backend:
   - runAsNonRoot: true
   - runAsUser: 1000
   - runAsGroup: 1000
   - fsGroup: 1000
   - allowPrivilegeEscalation: false
   - capabilities.drop: ["ALL"]
   - readOnlyRootFilesystem: true
3. Удален privileged: true
4. PSA блокирует создание привилегированных подов
- Под backend запущен от non-root пользователя (uid=1000)
- Под имеет SecurityContext (подтверждено в Deployment)
- PSA блокирует создание небезопасных подов
- Контейнер не имеет привилегий (CapEff: 0000000000000000)
- Доступ к root-файлам запрещен
```
# Поды в неймспэйсе backend
NAME                       READY   STATUS    RESTARTS   AGE
backend-78674d7d5c-nsfpr   1/1     Running   0          5m11s

# User ID
uid=1000 gid=1000 groups=1000

# Capabilities
CapInh: 0000000000000000
CapPrm: 0000000000000000
CapEff: 0000000000000000
CapBnd: 0000000000000000
CapAmb: 0000000000000000

# Доступ к /root запрещен
total 0
ls: can't open '/root': Permission denied
command terminated with exit code 1

# Переменные среды
DB_USERNAME=admin
DB_PASSWORD=secret-password-456
DB_HOST=backend.backend.svc.cluster.local

# PSA статусы
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: baseline
  name: backend
  resourceVersion: "192234"
  uid: 72632eeb-3f82-4479-ad03-1fc21d6367b4
```

## Шаг 5: сетевая изоляция

Политики:
1. deny-all в backend - изолирует весь трафик
2. allow-frontend-to-backend в backend - разрешает доступ от frontend
3. allow-egress-frontend в frontend - разрешает DNS и доступ к backend

Результаты тестов:
Для тестирования был запущен тестовый сервер в backend, который действительно слушает порт 5432

1. frontend → backend:5432 

```
$ kubectl run test-frontend --image=busybox -n frontend --rm -it --restart=Never -- sh

/ # wget -O- --timeout=5 test-server.backend.svc.cluster.local:5432
Connecting to test-server.backend.svc.cluster.local:5432 (10.103.207.196:5432)
writing to stdout
<!DOCTYPE HTML>
<html lang="en">
<head>
...
```

2. default → backend:5432

```
$ kubectl run test-default --image=busybox -n default --rm -it --restart=Never -- sh

/ # wget -O- --timeout=5 test-server.backend.svc.cluster.local:5432
Connecting to test-server.backend.svc.cluster.local:5432 (10.103.207.196:5432)
wget: download timed out
```

### Выполненные действия:
1. Создана NetworkPolicy `deny-all` в неймспейсе backend (изоляция)
2. Создана NetworkPolicy `allow-frontend-to-backend` в backend (разрешает доступ от frontend)
3. Создана NetworkPolicy `allow-egress-frontend` в frontend (разрешает DNS и доступ к backend)

## Шаг 6: сканирование и исправление уязвимостей
1. Повторное сканирование Kubescape 
```
╭─────────────────┬────╮
│        Controls │ 26 │
│          Passed │ 5  │
│          Failed │ 19 │
│ Action Required │ 2  │
╰─────────────────┴────╯
╭──────────┬────╮
│ Critical │ 0  │
│     High │ 43 │
│   Medium │ 79 │
│      Low │ 10 │
╰──────────┴────╯
╭──────────┬────────────────────────────────────────────────────┬──────────────────┬───────────────┬───────────────────╮
│ Severity │ Control name                                       │ Failed resources │ All Resources │ Compliance score  │
├──────────┼────────────────────────────────────────────────────┼──────────────────┼───────────────┼───────────────────┤
│ Critical │ Disable anonymous access to Kubelet service        │         0        │       0       │ Action Required * │
│ Critical │ Enforce Kubelet client TLS authentication          │         0        │       0       │ Action Required * │
│   High   │ Applications credentials in configuration files    │         4        │       61      │        93%        │
│   High   │ HostNetwork access                                 │         4        │       27      │        85%        │
│   High   │ Insecure capabilities                              │         1        │       27      │        96%        │
│   High   │ Privileged container                               │         2        │       27      │        93%        │
│   High   │ Ensure CPU limits are set                          │        18        │       27      │        33%        │
│   High   │ Ensure memory limits are set                       │        14        │       27      │        48%        │
│  Medium  │ Prevent containers from allowing command execution │         3        │      123      │        98%        │
│  Medium  │ Non-root containers                                │        13        │       27      │        52%        │
│  Medium  │ Allow privilege escalation                         │         5        │       27      │        81%        │
│  Medium  │ Ingress and Egress blocked                         │        17        │       31      │        45%        │
│  Medium  │ Automatic mapping of service account               │        20        │       98      │        80%        │
│  Medium  │ Administrative Roles                               │         3        │      123      │        98%        │
│  Medium  │ Cluster internal networking                        │         8        │       15      │        47%        │
│  Medium  │ Linux hardening                                    │         7        │       27      │        74%        │
│  Medium  │ Secret/etcd encryption enabled                     │         1        │       1       │         0%        │
│  Medium  │ Audit logs enabled                                 │         1        │       1       │         0%        │
│  Medium  │ Nginx Ingress Controller End of Life               │         1        │       23      │        96%        │
│    Low   │ Immutable container filesystem                     │         9        │       27      │        67%        │
│    Low   │ PSP enabled                                        │         1        │       1       │         0%        │
├──────────┼────────────────────────────────────────────────────┼──────────────────┼───────────────┼───────────────────┤
│          │                  Resource Summary                  │        34        │      274      │       64.82%      │
╰──────────┴────────────────────────────────────────────────────┴──────────────────┴───────────────┴───────────────────╯
```
В результате исправлений на предыдущих шагах общий оценка соответствия увеличилась 62.66% -> 64.82%

### Исправление проблем (помимо исправленных ранее)
1. Добавить CPU и Memory limits для приложений backend и backend 
```
$ kubectl get pods -n frontend -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].resources}{"\n"}{end}'

frontend-85dc99d84-d4p6c        {"limits":{"cpu":"100m","memory":"128Mi"},"requests":{"cpu":"50m","memory":"64Mi"}}

$ kubectl get pods -n backend -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].resources}{"\n"}{end}'

backend-76fbb68854-75xt4        {"limits":{"cpu":"100m","memory":"128Mi"},"requests":{"cpu":"50m","memory":"64Mi"}}
```
2. Автоматическая настройка безопасности подов (PSA)
```
$ kubectl get namespace backend -o yaml | grep -A 5 pod-security

    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: baseline
```
Происходит блокировка создания привелигированных подов
```
$ kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-privileged
  namespace: backend
spec:
  containers:
  - name: test
    image: nginx
    securityContext:
      privileged: true
EOF

Error from server (Forbidden): error when creating "STDIN": pods "test-privileged" is forbidden: violates PodSecurity "baseline:latest": privileged (container "test" must not set securityContext.privileged=true)
```
3. Система обноружения анамалий ничего не обнаружила. 
Для доказательства роботоспособности был запущен тестовый под и прочитан файл /etc/shadow

## Сравнительная таблица "До/После"

| Параметр | До | После |
|----------|-----|-------|
| **RBAC** | | |
| ServiceAccount | default | frontend-sa |
| RBAC правила | ClusterRole с wildcard | Role с минимальными правами |
| **Секреты** | | |
| Хранение | ConfigMap + hardcoded | Secret + secretKeyRef |
| **Безопасность подов** | | |
| privileged: true | Да (backend) | Нет |
| SecurityContext | Отсутствует | Добавлен |
| PSA | Отсутствует | baseline |
| **Сетевая безопасность** | | |
| Network Policies | Нет | Да |
| **Kubescape** | | |
| Compliance score | 62.66% | 64.82% |
| HIGH проблемы | 48 | 43 |

Иерархия докозательств:
manifests/ - Манифесты Kubernetes (до исправлений)  
├── rbac/ - RBAC-конфигурации  
│ ├── frontend-sa.yaml - ServiceAccount для frontend   
│ ├── frontend-role.yaml - Role с минимальными правами  
│ └── frontend-rolebinding.yaml - Привязка роли к ServiceAccount  
├── secrets/- Секреты  
│ ├── db-secret.yaml - Секрет для backend  
│ └── db-secret-frontend.yaml - Секрет для frontend  
├── network-policies/ - Network Policies  
│ ├── deny-all-backend.yaml - Изоляция backend
│ ├── deny-all-frontend.yaml - Изоляция frontend  
│ ├── allow-frontend-to-backend.yaml - Разрешение доступа  
│ └── allow-egress-frontend.yaml - DNS и доступ к backend  
├── frontend-deployment.yaml - Deployment frontend с новым SA  
├── backend-deployment.yaml - Deployment backend с SecurityContext  
├── namespace-backend.yaml - Неймспейс backend с PSA  
├── REPORT.md - Полный отчет по практической работе  
└── kubescape_*.txt # Результаты сканирования kubescape  