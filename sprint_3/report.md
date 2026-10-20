# Отчёт по аудиту безопасности Linux-сервера

**Автор:** Svetlana Golub  
**Дата аудита:** 25.06.2026  
**Целевая система:** Debian 12, [81.26.188.120/fv419j3vupl0apbktqqf]

---

## 1. Общая информация о системе

| Параметр | Значение |
|---|---|
| ОС | Debian GNU/Linux 12 |
| Версия ядра | 6.1.0-44-amd64 |
| Hostname | fv419j3vupl0apbktqqf |
| IP-адрес | 81.26.188.120 |
| Активных сервисов | 41 |
| Открытых портов | 8 |
| Пользователей | 7 (-v "nologin\|false") |

### 1.1 Открытые порты

```bash
$ ss -tuln
Netid        State         Recv-Q         Send-Q                                    Local Address:Port                  Peer Address:Port        Process        
udp          UNCONN        0              0                                               0.0.0.0:68                         0.0.0.0:*                          
udp          UNCONN        0              0                                               0.0.0.0:68                         0.0.0.0:*                          
udp          UNCONN        0              0                                           10.130.0.93:123                        0.0.0.0:*                          
udp          UNCONN        0              0                                             127.0.0.1:123                        0.0.0.0:*                          
udp          UNCONN        0              0                                               0.0.0.0:123                        0.0.0.0:*                          
udp          UNCONN        0              0                      [fe80::d20d:14ff:fecc:7ff6]%eth0:123                           [::]:*                          
udp          UNCONN        0              0                                                 [::1]:123                           [::]:*                          
udp          UNCONN        0              0                                                  [::]:123                           [::]:*                          
tcp          LISTEN        0              5                                               0.0.0.0:8080                       0.0.0.0:*                          
tcp          LISTEN        0              5                                               0.0.0.0:8081                       0.0.0.0:*                          
tcp          LISTEN        0              128                                           127.0.0.1:44451                      0.0.0.0:*                          
tcp          LISTEN        0              128                                           127.0.0.1:46353                      0.0.0.0:*                          
tcp          LISTEN        0              20                                            127.0.0.1:25                         0.0.0.0:*                          
tcp          LISTEN        0              128                                             0.0.0.0:22                         0.0.0.0:*                          
tcp          LISTEN        0              20                                                [::1]:25                            [::]:*                          
tcp          LISTEN        0              128                                                [::]:22                            [::]:* 
```

| Порт | Протокол | Сервис | Необходим? | Комментарий |
|---|---|---|---|---|
| 22 | TCP | SSH | Да | Основной доступ |
| 25 | TCP | SNMP | Нет | Почтовый сервер, слушает только localhost, но запущен без необходимости |
| 68 | UDP | DHCP Client | Да | Получение IP-адреса |
| 123 | UDP | NTP | Да | Синхронизация времени |
| 8080 | TCP | SimpleHTTPServer  | Нет | Опасный HTTP-сервер без аутентификации, слушает на всех интерфейсах |
| 8081 | TCP | SimpleHTTPServer  | Нет | Опасный HTTP-сервер без аутентификации, слушает на всех интерфейсах |
| 44451 | TCP | VSCode Server | Да | Только локально, нужен для работы в VSCode |
| 46353 | TCP | VSCode Server | Да | Только локально, нужен для работы в VSCode |

### 1.2 Активные сервисы

```bash
$ systemctl list-units --type=service --state=active
  UNIT                               LOAD   ACTIVE SUB DESCRIPTION                                      
  auditd.service                     loaded active running Security Auditing Service
  c2-client.service                  loaded active running DNS resolution helper
  cloud-config.service               loaded active exited  Apply the settings specified in cloud-config
  cloud-final.service                loaded active exited  Execute cloud user/final scripts
  cloud-init-local.service           loaded active exited  Initial cloud-init job (pre-networking)
  cloud-init.service                 loaded active exited  Initial cloud-init job (metadata service crawler)
  console-setup.service              loaded active exited  Set console font and keymap
  cron.service                       loaded active running Regular background program processing daemon
  dbus.service                       loaded active running D-Bus System Message Bus
  exim4.service                      loaded active running LSB: exim Mail Transport Agent
  getty@tty1.service                 loaded active running Getty on tty1
  ifup@eth0.service                  loaded active exited  ifup for eth0
  ifupdown-pre.service               loaded active exited  Helper to synchronize boot up for ifupdown
  insecure-httpd.service             loaded active running Internal web application
  insecure-httpd2.service            loaded active running Internal API service
  keyboard-setup.service             loaded active exited  Set the console keyboard layout
  kmod-static-nodes.service          loaded active exited  Create List of Static Device Nodes
  network-scanner.service            loaded active running Network health checker
  networking.service                 loaded active exited  Raise network interfaces
  ntpsec.service                     loaded active running Network Time Service
  root-service.service               loaded active running System maintenance service
  serial-getty@ttyS0.service         loaded active running Serial Getty on ttyS0
  ssh.service                        loaded active running OpenBSD Secure Shell server
  suspicious-process.service         loaded active running System monitoring helper
  systemd-binfmt.service             loaded active exited  Set Up Additional Binary Formats
  systemd-journal-flush.service      loaded active exited  Flush Journal to Persistent Storage
  systemd-journald.service           loaded active running Journal Service
  systemd-logind.service             loaded active running User Login Management
  systemd-modules-load.service       loaded active exited  Load Kernel Modules
  systemd-random-seed.service        loaded active exited  Load/Save Random Seed
  systemd-remount-fs.service         loaded active exited  Remount Root and Kernel File Systems
  systemd-sysctl.service             loaded active exited  Apply Kernel Variables
  systemd-sysusers.service           loaded active exited  Create System Users
  systemd-tmpfiles-setup-dev.service loaded active exited  Create Static Device Nodes in /dev
  systemd-tmpfiles-setup.service     loaded active exited  Create System Files and Directories
  systemd-udev-trigger.service       loaded active exited  Coldplug All udev Devices
  systemd-udevd.service              loaded active running Rule-based Manager for Device Events and Files
  systemd-update-utmp.service        loaded active exited  Record System Boot/Shutdown in UTMP
  systemd-user-sessions.service      loaded active exited  Permit User Sessions
  user-runtime-dir@1000.service      loaded active exited  User Runtime Directory /run/user/1000
  user@1000.service                  loaded active running User Manager for UID 1000
```

---

## 2. Результаты инструментов аудита

### 2.1 Lynis

```bash
$ sudo lynis audit system
# Общий балл: 60/100
# Предупреждений: 3
# Рекомендаций: 55
```

**Ключевые предупреждения (анализ наиболее важных, три и более):**

1. `[AUTH-9283]` - Обнаружены учётные записи без пароля. Это критическая уязвимость, так как позволяет получить доступ к системе без аутентификации. Необходимо откорректировать парольную политику, либо заблокировать/удалить неиспользуемые аккаунты.
2. `[NETW-2705]` - Не найдено двух работающих DNS-серверов. Это проблема отказоустойчивости и производительности сети. При отказе одного DNS-сервера создаётся риск недоступности сети и сбоев в работе сервисов. Необходимо настроить как минимум два корректно работающих DNS-сервера.
3. `[FINT-4316]` - Отсутствует база данных для AIDE. Это снижает возможности системы по обнаружению вторжений и контролю целостности файлов. Необходимо инициализировать базу данных AIDE и настроить её регулярное обновление и проверку.

### 2.2 `nmap`

```bash
$ nmap -sV -sC localhost
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
| ssh-hostkey: 
|   256 e0fe38b1e8214a1ede02bbd0e5c439c8 (ECDSA)
|_  256 d6ef550c2b0f3a5df4e38161797fac9c (ED25519)
25/tcp   open  smtp    Exim smtpd 4.96
| smtp-commands: fv419j3vupl0apbktqqf.auto.internal Hello localhost [127.0.0.1], SIZE 52428800, 8BITMIME, PIPELINING, PIPECONNECT, CHUNKING, STARTTLS, PRDR, HELP
|_ Commands supported: AUTH STARTTLS HELO EHLO MAIL RCPT DATA BDAT NOOP QUIT RSET HELP
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=fv419j3vupl0apbktqqf.auto.internal/organizationName=Exim Developers/countryName=UK
| Not valid before: 2026-06-25T16:12:28
|_Not valid after:  2026-06-25T18:12:28
8080/tcp open  http    SimpleHTTPServer 0.6 (Python 3.11.2)
|_http-server-header: SimpleHTTP/0.6 Python/3.11.2
|_http-title: Directory listing for /
8081/tcp open  http    SimpleHTTPServer 0.6 (Python 3.11.2)
|_http-server-header: SimpleHTTP/0.6 Python/3.11.2
|_http-title: Directory listing for /
Service Info: Host: fv419j3vupl0apbktqqf.auto.internal; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

### 2.3 `chkrootkit`

```bash
$ sudo chkrootkit
WARNING: The following suspicious files and directories were found:
/usr/lib/ruby/vendor_ruby/rubygems/optparse/.document
/usr/lib/ruby/vendor_ruby/rubygems/ssl_certs/.document
/usr/lib/ruby/vendor_ruby/rubygems/tsort/.document
/usr/lib/ruby/gems/3.1.0/gems/typeprof-0.21.2/vscode/.vscodeignore
/usr/lib/ruby/gems/3.1.0/gems/typeprof-0.21.2/vscode/.vscode
/usr/lib/ruby/gems/3.1.0/gems/typeprof-0.21.2/vscode/.gitignore
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/basic/file/.htpasswd
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/basic/file/.htaccess
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/basic/authz_owner/.htpasswd
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/basic/authz_owner/.htaccess
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/noentry/.htaccess
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest_time/.htpasswd
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest_time/.htaccess
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest_anon/.htpasswd
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest_anon/.htaccess
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest/.htpasswd
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest/.htaccess
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest_wrongrelm/.htpasswd
/usr/lib/python3/dist-packages/fail2ban/tests/files/config/apache-auth/digest_wrongrelm/.htaccess

WARNING: Possible Linux.Xor.DDoS installed:
/tmp/suspicious.sh
/tmp/dangerous_file
/tmp/root_created_file

WARNING: Output from ifpromisc:
lo: not promisc and no packet sniffer sockets
eth0: PACKET SNIFFER(/usr/sbin/dhclient[498], /usr/sbin/dhclient[462])
```
Добавлены только WARNING

### 2.4 `aide`

```bash
# Cначала инициализация бд
$ sudo aideinit
$ sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
# Результат
$ sudo aide --config /etc/aide/aide.conf --check
Summary:
  Total number of entries:      60809
  Added entries:                0
  Removed entries:              0
  Changed entries:              11

---------------------------------------------------
Changed entries:
---------------------------------------------------

f =.... mc.. .. . : /home/debian/.vscode-server/data/User/workspaceStorage/121504bfd3f675d88eaf7d22f3902e81/vscode.lock
f =.... mc.. .. . : /tmp/c2_data.txt
f =.... mc..... . : /tmp/dangerous_file
f =.... mc..... . : /tmp/passwd_backup
f =.... mc.. .. . : /tmp/root_created_file
f =.... mc..... . : /tmp/suspicious.sh
f >b... mc..+.. . : /var/log/aide/aideinit.errors
f >b... mc..H.. . : /var/log/aide/aideinit.log
f >b... mc.. .. . : /var/log/audit/audit.log
f >b... mc.. .. . : /var/log/root_service.log
f >b... mc.. .. . : /var/log/suspicious_scan.log  
```

### 2.5 `fail2ban`

```bash
$ sudo systemctl status fail2ban
     Loaded: loaded (/lib/systemd/system/fail2ban.service; enabled; preset: enabled)
     Active: failed (Result: exit-code) since Thu 2026-06-25 16:12:27 UTC; 1h 26min ago
   Duration: 280ms
       Docs: man:fail2ban(1)
    Process: 568 ExecStart=/usr/bin/fail2ban-server -xf start (code=exited, status=255/EXCEPTION)
   Main PID: 568 (code=exited, status=255/EXCEPTION)
        CPU: 86ms
```

### 2.6 `auditd`

```bash
# Правила, которое вы настроили:
$ sudo auditctl -l
-w /etc -p wa -k config_changes
-w /var/log -p wa -k log_changes
-a always,exit -S execve -F key=process_creation
-a always,exit -S chmod,fchmod -F key=perm_mod
-a always,exit -F arch=b64 -S execve -F key=process_creation
-a always,exit -F arch=b64 -S chmod,fchmod -F key=perm_mod
-a always,exit -F arch=b64 -S chown,fchown,lchown -F key=perm_owner

# Пример обнаруженного события:
$ sudo ausearch -k config_changes
time->Thu Jun 25 17:47:39 2026
type=PROCTITLE msg=audit(1782409659.879:2129): proctitle=746F756368002F6574632F746573745F636F6E666967
type=PATH msg=audit(1782409659.879:2129): item=1 name="/etc/test_config" inode=2559 dev=fe:02 mode=0100644 ouid=0 ogid=0 rdev=00:00 nametype=CREATE cap_fp=0 cap_fi=0 cap_fe=0 cap_fver=0 cap_frootid=0
type=PATH msg=audit(1782409659.879:2129): item=0 name="/etc/" inode=12 dev=fe:02 mode=040755 ouid=0 ogid=0 rdev=00:00 nametype=PARENT cap_fp=0 cap_fi=0 cap_fe=0 cap_fver=0 cap_frootid=0
type=CWD msg=audit(1782409659.879:2129): cwd="/home/debian"
type=SYSCALL msg=audit(1782409659.879:2129): arch=c000003e syscall=257 success=yes exit=3 a0=ffffff9c a1=7ffcfa7bb7d9 a2=941 a3=1b6 items=2 ppid=124513 pid=124514 auid=1000 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts1 ses=1 comm="touch" exe="/usr/bin/touch" subj=unconfined key="config_changes"
```

### 2.7 Дополнительные инструменты

Укажите, какой дополнительный инструмент использовали и что обнаружили:

```bash
# Инструмент: rkhunter
# Команда и результат:
$ sudo rkhunter --check --skip-keypress
Warning: Passwordless accounts
Warning: SSH root access is allowed          

```

---

## 3. Обнаруженные проблемы безопасности

### Проблема #1: SSH разрешает вход root и пустые пароли

| | |
|---|---|
| **Критичность** | Critical  |
| **Категория** | Доступ |
| **Инструмент обнаружения** | lynis, подтверждение — ручная проверка конфигурации |

**Доказательство:**

```bash
$ grep -E "PermitRootLogin|PasswordAuthentication|PermitEmptyPasswords" /etc/ssh/sshd_config
PermitRootLogin yes
PermitEmptyPasswords yes
PasswordAuthentication yes
```

**Анализ:** 
PermitRootLogin yes — разрешён вход root по SSH
PermitEmptyPasswords yes — разрешены пустые пароли
PasswordAuthentication yes — разрешена аутентификация по паролю

Можно подобрать пароль к root или войти с пустым паролем. Без fail2ban (#5) и фаервола (#3) это прямой путь к компрометации.

**Связанные проблемы:** #3 (нет фаервола), #5 (fail2ban не работает), #6 (отключены автообновления)

**Рекомендация:**

```bash
PermitRootLogin no
PermitEmptyPasswords no
PasswordAuthentication no

sudo systemctl restart sshd
```

---

### Проблема #2: Опасные права у файлов /etc/passwd и /etc/shadow

| | |
|---|---|
| **Критичность** | Critical |
| **Категория** | Доступ |
| **Инструмент обнаружения** | lynis, подтверждение — ручная проверка прав файлов |

**Доказательство:**

```bash
$ ls -la /etc/passwd /etc/shadow
-rw-rw-r-- 1 root root   1498 Jun 24 19:33 /etc/passwd
-rw-rw-r-- 1 root shadow 1004 Jun 24 19:33 /etc/shadow
```

**Анализ:** 
/etc/passwd имеет права 664 вместо правильных 644
/etc/shadow имеет права 664 вместо правильных 640
Это позволяет группе записывать в файлы паролей, что может привести к созданию новых пользователей или изменению паролей существующих.

**Связанные проблемы:** #1 (SSH уязвимости), #6 (отключены автообновления)

**Рекомендация:**

```bash
sudo chmod 644 /etc/passwd
sudo chmod 640 /etc/shadow
```

---

### Проблема #3: Отсутствует фаервол

| | |
|---|---|
| **Критичность** | High |
| **Категория** | Сеть |
| **Инструмент обнаружения** | lynis, подтверждение — ручная проверка статуса UFW |

**Доказательство:**

```bash
$ ufw status
bash: ufw: command not found
```

**Анализ:**
UFW даже не установлен на сервере. Все открытые порты доступны извне без какой-либо фильтрации.

**Связанные проблемы:** #1 (SSH), #4 (подозрительные Python сервисы), #6 (отключены автообновления)

**Рекомендация:**

```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw --force enable
```

---

### Проблема #4: Запущены подозрительные Python-скрипты от root
| | |
|---|---|
| **Критичность** | Critical |
| **Категория** | Процессы |
| **Инструмент обнаружения** | ps aux |

**Доказательство:**

```bash
$ ps aux
root         561  0.0  0.2  18308 11964 ?        Ss   10:42   0:00 /usr/bin/python3 /usr/local/bin/c2_client.py
root         568  0.0  0.4  28304 18956 ?        Ss   10:42   0:00 /usr/bin/python3 /usr/local/bin/insecure_httpd.py
root         569  0.0  0.4  27248 18748 ?        Ss   10:42   0:00 /usr/bin/python3 /usr/local/bin/insecure_httpd2.py
root         570  0.0  0.0   7072  3288 ?        Ss   10:42   0:00 /bin/bash /usr/local/bin/network_scanner.sh
root         575  0.0  0.0   6940  3168 ?        Ss   10:42   0:00 /bin/bash /usr/local/bin/root_service.sh
root         579  0.0  0.0   6940  3188 ?        Ss   10:42   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        1160  0.0  0.0   2584   956 ?        Ss   10:45   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        1161  0.0  0.0   6940  3164 ?        S    10:45   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        1590  0.0  0.0   2584   956 ?        Ss   10:50   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        1591  0.0  0.0   6940  3280 ?        S    10:50   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        2018  0.0  0.0   2584   916 ?        Ss   10:55   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        2019  0.0  0.0   6940  3232 ?        S    10:55   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        3362  0.0  0.0   2584   936 ?        Ss   11:00   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        3364  0.0  0.0   6940  3192 ?        S    11:00   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        3925  0.0  0.0   2584   920 ?        Ss   11:05   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        3926  0.0  0.0   6940  3296 ?        S    11:05   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        4789  0.0  0.0   2584   896 ?        Ss   11:10   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        4791  0.0  0.0   6940  3288 ?        S    11:10   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        6122  0.0  0.0   2584   916 ?        Ss   11:15   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        6123  0.0  0.0   6940  3328 ?        S    11:15   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
```

**Анализ:** 
Названия файлов и сервисов явно указывают на вредоносное ПО. Атакующий уже имеет контроль над сервером и использует его для получения команд, передачи данных и создания бэкдоров.

**Связанные проблемы:**  #3 (отсутствует файрвол), #6 (отключены автообновления), #7 (файлы в /tmp)

**Рекомендация:**

```bash
sudo kill 561 568 569 570 575 579 1160 1161 1590 1591 2018 2019 3362 3364 3925 3926 4789 4791 6122 6123
sudo rm -f /usr/local/bin/c2_client.py /usr/local/bin/insecure_httpd.py /usr/local/bin/insecure_httpd2.py /usr/local/bin/network_scanner.sh /usr/local/bin/root_service.sh /usr/local/bin/suspicious_process.sh
sudo systemctl stop c2-client insecure-httpd insecure-httpd2 network-scanner root-service suspicious-process
sudo systemctl disable c2-client insecure-httpd insecure-httpd2 network-scanner root-service suspicious-process
sudo rm -f /etc/systemd/system/c2-client.service /etc/systemd/system/insecure-httpd.service /etc/systemd/system/insecure-httpd2.service /etc/systemd/system/network-scanner.service /etc/systemd/system/root-service.service /etc/systemd/system/suspicious-process.service
sudo systemctl daemon-reload
```

---

### Проблема #5: Fail2ban установлен, но не работает

| | |
|---|---|
| **Критичность** | High |
| **Категория** | Доступ |
| **Инструмент обнаружения** | systemctl status |

**Доказательство:**

```bash
$ sudo systemctl status fail2ban
× fail2ban.service - Fail2Ban Service
     Loaded: loaded (/lib/systemd/system/fail2ban.service; enabled; preset: enabled)
     Active: failed (Result: exit-code) since Thu 2026-06-25 16:12:27 UTC; 3h 14min ago
    Process: 568 ExecStart=/usr/bin/fail2ban-server -xf start (code=exited, status=255/EXCEPTION)
```

**Анализ:** 
Fail2ban должен защищать от брутфорс-атак, но не работает, потому что не может найти лог-файл SSH (/var/log/auth.log). Это может быть связано с неправильной конфигурацией fail2ban. В сочетании с PermitRootLogin yes и PasswordAuthentication yes (проблема #1) атакующий может бесконечно перебирать пароли без риска быть заблокированным.

**Связанные проблемы:** #1 (SSH уязвимости), #6 (отключены автообновления)

**Рекомендация:**

```bash
# Настройка fail2ban для работы с systemd-journald
sudo tee /etc/fail2ban/jail.local <<'EOF'
[DEFAULT]
backend = systemd
bantime = 1h
findtime = 10m
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
maxretry = 3
EOF

# Затем перезапускаем fail2ban
sudo systemctl restart fail2ban
```

---

### Проблема #6: Отключены автоматические обновления безопасности

| | |
|---|---|
| **Критичность** | Medium |
| **Категория** | Конфигурация |
| **Инструмент обнаружения** | systemctl status |

**Доказательство:**

```bash
$ systemctl status unattended-upgrades
○ unattended-upgrades.service - Unattended Upgrades Shutdown
     Loaded: loaded (/lib/systemd/system/unattended-upgrades.service; disabled; preset: enabled)
     Active: inactive (dead)
```

**Анализ:** 
Система не получает автоматические исправления для известных уязвимостей (CVE). При появлении нового эксплойта для Exim, OpenSSL или других компонентов сервер остаётся уязвимым до тех пор, пока администратор не установит обновления вручную. В условиях, когда на сервере уже обнаружен C2-клиент (#4), отсутствие автообновлений даёт злоумышленнику дополнительное время для эксплуатации уязвимостей и закрепления в системе.

**Связанные проблемы:** #1 (SSH уязвимости), #3 (отсутствие файрвола), #4 (C2 клиент), #7 (файлы в /tmp)

**Рекомендация:**

```bash
# Включаем unattended-upgrades, но с чёрным списком для критичных сервисов
$ sudo tee /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

$ sudo tee /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Package-Blacklist {
    "mysql-server";
    "postgresql";
    "nginx";
    "apache2";
    "php";
    "python3";
    "docker";
};
EOF
```

---

### Проблема #7: Подозрительные файлы в /tmp

| | |
|---|---|
| **Критичность** | Critical |
| **Категория** | Процессы |
| **Инструмент обнаружения** | chkrootkit - подтверждение ручной проверкой файлов |

**Доказательство:**

```bash
$ ls -la /tmp/suspicious.sh /tmp/dangerous_file /tmp/root_created_file
-rwxr-xr-x 1 root root 1024 Jun 25 16:12 /tmp/suspicious.sh
-rw-r--r-- 1 root root  512 Jun 25 16:12 /tmp/dangerous_file
-rw-r--r-- 1 root root  256 Jun 25 16:12 /tmp/root_created_file
```

**Анализ:** 
Файлы в /tmp указывают на ботнет Linux.Xor.DDoS. Сервер уже используется для проведения DDoS-атак. В сочетании с C2-клиентом (проблема #4) это подтверждает полную компрометацию системы и участие сервера в незаконных сетевых атаках. Отсутствие автообновлений (проблема #6) позволяет злоумышленнику использовать старые уязвимости для поддержания контроля.

**Связанные проблемы:** #4 (C2 клиент), #6 (отключены автообновления)

**Рекомендация:**

```bash
$ sudo rm -f /tmp/suspicious.sh /tmp/dangerous_file /tmp/root_created_file /tmp/c2_data.txt /tmp/passwd_backup
```

---

### Проблема #8: Открыты порты 8080 и 8081 с небезопасными HTTP-серверами (Python SimpleHTTPServer)
| | |
|---|---|
| **Критичность** | Critical |
| **Категория** | Сеть |
| **Инструмент обнаружения** | nmap - подтверждение ручной проверкой открытых портов |

**Доказательство:**

```bash
$ sudo nmap -sV -sC -p 8080,8081 localhost
PORT     STATE SERVICE VERSION
8080/tcp open  http    SimpleHTTPServer 0.6 (Python 3.11.2)
|_http-title: Directory listing for /
|_http-server-header: SimpleHTTP/0.6 Python/3.11.2
8081/tcp open  http    SimpleHTTPServer 0.6 (Python 3.11.2)
|_http-title: Directory listing for /
|_http-server-header: SimpleHTTP/0.6 Python/3.11.2

$ ss -tuln | grep -E "8080|8081"
tcp   LISTEN 0      5                               0.0.0.0:8080       0.0.0.0:*          
tcp   LISTEN 0      5                               0.0.0.0:8081       0.0.0.0:*
```

**Анализ:** 
Два Python SimpleHTTPServer запущены от root и слушают на всех интерфейсах, что делает их доступными извне. В сочетании с отсутствием фаервола (#3) это создаёт прямой вектор атаки для получения доступа к файловой системе сервера.

**Связанные проблемы:** #3 (отсутствие фаервола), #4 (C2 клиент)

**Рекомендация:**

```bash
sudo pkill -f "python3 -m http.server"
sudo pkill -f "SimpleHTTPServer"
```

---

## 4. Устранённые проблемы

### Исправление #1: Запущены подозрительные Python-скрипты от root

**Что сделано и почему:** 
На сервере обнаружено множество подозрительных процессов, запущенных от root: C2-клиент, небезопасные HTTP-серверы, скрипты сканирования сети, root-сервис и подозрительные процессы, запускаемые через cron каждые 5 минут. Все процессы остановлены.

**Команды исправления:**

```bash
sudo kill 561 568 569 570 575 579 1160 1161 1590 1591 2018 2019 3362 3364 3925 3926 4789 4791 6122 6123
sudo rm -f /usr/local/bin/c2_client.py /usr/local/bin/insecure_httpd.py /usr/local/bin/insecure_httpd2.py /usr/local/bin/network_scanner.sh /usr/local/bin/root_service.sh /usr/local/bin/suspicious_process.sh
sudo systemctl stop c2-client insecure-httpd insecure-httpd2 network-scanner root-service suspicious-process
sudo systemctl disable c2-client insecure-httpd insecure-httpd2 network-scanner root-service suspicious-process
sudo rm -f /etc/systemd/system/c2-client.service /etc/systemd/system/insecure-httpd.service /etc/systemd/system/insecure-httpd2.service /etc/systemd/system/network-scanner.service /etc/systemd/system/root-service.service /etc/systemd/system/suspicious-process.service
sudo systemctl daemon-reload
```

**До исправления:**

```bash
$ ps aux | grep -E "c2_client|insecure_httpd|network_scanner|root_service|suspicious_process" | grep -v grep
root         561  0.0  0.2  18308 11964 ?        Ss   10:42   0:00 /usr/bin/python3 /usr/local/bin/c2_client.py
root         568  0.0  0.4  28304 18956 ?        Ss   10:42   0:00 /usr/bin/python3 /usr/local/bin/insecure_httpd.py
root         569  0.0  0.4  27248 18748 ?        Ss   10:42   0:00 /usr/bin/python3 /usr/local/bin/insecure_httpd2.py
root         570  0.0  0.0   7072  3288 ?        Ss   10:42   0:00 /bin/bash /usr/local/bin/network_scanner.sh
root         575  0.0  0.0   6940  3168 ?        Ss   10:42   0:00 /bin/bash /usr/local/bin/root_service.sh
root         579  0.0  0.0   6940  3188 ?        Ss   10:42   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        1160  0.0  0.0   2584   956 ?        Ss   10:45   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        1161  0.0  0.0   6940  3164 ?        S    10:45   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        1590  0.0  0.0   2584   956 ?        Ss   10:50   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        1591  0.0  0.0   6940  3280 ?        S    10:50   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        2018  0.0  0.0   2584   916 ?        Ss   10:55   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        2019  0.0  0.0   6940  3232 ?        S    10:55   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        3362  0.0  0.0   2584   936 ?        Ss   11:00   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        3364  0.0  0.0   6940  3192 ?        S    11:00   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        3925  0.0  0.0   2584   920 ?        Ss   11:05   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        3926  0.0  0.0   6940  3296 ?        S    11:05   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        4789  0.0  0.0   2584   896 ?        Ss   11:10   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        4791  0.0  0.0   6940  3288 ?        S    11:10   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
root        6122  0.0  0.0   2584   916 ?        Ss   11:15   0:00 /bin/sh -c /usr/local/bin/suspicious_process.sh
root        6123  0.0  0.0   6940  3328 ?        S    11:15   0:00 /bin/bash /usr/local/bin/suspicious_process.sh
```

**После исправления:**

```bash
$ ps aux | grep -E "c2_client|insecure_httpd|network_scanner|root_service|suspicious_process" | grep -v grep
# Пустой вывод
```

---

### Исправление #2: Исправление SSH-конфигурации

**Что сделано и почему:** 
SSH разрешал вход root, пустые пароли и парольную аутентификацию. Это создавало прямой вектор для брутфорс-атак. После исправления вход root запрещён, пустые пароли отключены, разрешена только аутентификация по ключам.

**Команды исправления:**

```bash
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/PermitEmptyPasswords yes/PermitEmptyPasswords no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

sudo systemctl restart sshd
```

**До исправления:**

```bash
grep -E "PermitRootLogin|PasswordAuthentication|PermitEmptyPasswords" /etc/ssh/sshd_config
PermitRootLogin yes
PermitEmptyPasswords yes
PermitRootLogin yes
PasswordAuthentication yes
```

**После исправления:**

```bash
grep -E "PermitRootLogin|PasswordAuthentication|PermitEmptyPasswords" /etc/ssh/sshd_config
PermitRootLogin no
PermitEmptyPasswords no
PermitRootLogin no
PasswordAuthentication no
```

---

### Исправление #3: Опасные права у файлов /etc/passwd и /etc/shadow

**Что сделано и почему:** 
Обнаружены небезопасные права 664 на файлах /etc/passwd и /etc/shadow, что позволяло группе root записывать в эти файлы. Исправлены права на безопасные значения.

**Команды исправления:**

```bash
sudo chmod 644 /etc/passwd
sudo chmod 640 /etc/shadow
```

**До исправления:**

```bash
$ ls -la /etc/passwd /etc/shadow
-rw-rw-r-- 1 root root   1498 Jun 24 19:33 /etc/passwd
-rw-rw-r-- 1 root shadow 1004 Jun 24 19:33 /etc/shadow
```

**После исправления:**

```bash
$ ls -la /etc/passwd /etc/shadow
-rw-r--r-- 1 root root   1498 Jun 24 19:33 /etc/passwd
-rw-r----- 1 root shadow 1004 Jun 24 19:33 /etc/shadow
```
---

### Дополнительные исправления 

Все проблемы, описанные выше так же успешно устранены по рекомендациям из того же раздела. Также были закрыты ненужные порты через фаервол и завершены процессы, удалены подозрительные пользователи (процессы от них не запущены), пароли системных пользователей заблокированы. Настроила политику паролей. Изменила конфигурацию AIDE

```bash
sudo ufw deny 25/tcp
sudo systemctl stop exim4
sudo systemctl disable exim4

sudo passwd -l systemd-network
sudo passwd -l messagebus
sudo passwd -l sshd
sudo passwd -l ntpsec
sudo passwd -l tcpdump
sudo passwd -l Debian-exim
sudo passwd -l _aide

ps aux | grep -E "weakuser|adminuser|testuser|emptyuser" | grep -v grep
debian@fv419j3vupl0apbktqqf:~$ sudo userdel -r weakuser
sudo userdel -r adminuser
sudo userdel -r testuser
sudo userdel -r emptyuser

sudo sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/' /etc/login.defs
sudo sed -i 's/^PASS_MIN_DAYS.*/PASS_MIN_DAYS 7/' /etc/login.defs
sudo sed -i 's/^UMASK.*/UMASK 027/' /etc/login.defs

sudo tee -a /etc/aide/aide.conf <<'EOF'
All = p+i+n+u+g+s+m+c+acl+selinux+xattrs+sha512
EOF
```

## 5. Оценка рисков

### 5.1 Общий уровень безопасности

| Метрика | До харденинга | После исправлений |
|---|---|---|
| Lynis-балл | 60 | 72 |
| Критичных проблем | 5 | 0 |
| Открытых портов | 7 | 5 |

### 5.2 Приоритетные направления

Укажите, что **ещё** необходимо исправить (помимо уже устранённого) в порядке приоритета:

1. **[Critical/High]** — Настроить пароль на GRUB (BOOT-5122) для защиты от загрузки в однопользовательском режиме без аутентификации. Это позволит злоумышленнику с физическим доступом обойти все средства защиты и получить root-доступ.
2. **[High/Medium]** — Включить process accounting (ACCT-9622) для аудита всех выполняемых команд и действий пользователей. Это критически важно для расследования инцидентов и обнаружения аномальной активности.
3. **[Medium]** — Разместить /home, /tmp, /var на отдельных разделах (FILE-6310). Это защитит систему от отказа при полном заполнении одного из разделов и позволит настроить разные параметры монтирования (например, noexec для /tmp).

### 5.3 Вывод

В результате проведённого аудита безопасности Linux-сервера были выявлены и устранены 8 критических и высокорисковых уязвимостей
После применения всех исправлений Hardening index Lynis вырос с 60 до 72, что свидетельствует о значительном повышении уровня безопасности системы. Все критические предупреждения устранены.

Сервер готов к продакшну с оговорками, необходимо исправить недочёты из пункта 5.2. 

---

## Артефакты

В папке `/artifacts` находятся подпапки before, after и changed:

`/before`:
  - `lynis-before-report.txt` - полный отчёт Lynis до аудита;
  - `nmap-scan.txt` - результат сканирования `nmap` до аудита;
  - `aide-scan.txt` - результат сканирования `aide` до аудита;
  - `chkrootkit.txt` - результат сканирования `chkrootkit` до аудита

`/after`:
  - `lynis-after-report.txt` - полный отчёт Lynis после аудита;
  - `nmap-scan-after.txt` - результат сканирования `nmap` после аудита;
  - `aide-scan-after.txt` - результат сканирования `aide` после аудита;
  - `chkrootkit-after.txt` - результат сканирования `chkrootkit` после аудита;
  - `rkhunter-after.txt` - результат сканирования `rkhunter` после аудита

  `/changed`:
  - `sshd_config` — конфигурация SSH 
  - `login.defs` — политика паролей 
  - `fail2ban-jail.local` — конфигурация fail2ban
  - `20auto-upgrades` — настройки автоматических обновлений
  - `50unattended-upgrades` — настройки обновлений безопасности
