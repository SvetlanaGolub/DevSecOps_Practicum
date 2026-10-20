
| Роль   | Repo/MR (ветки/ревью) | Registry | Deploy |
| ------ | ----------            | -------- | -------|
| Developer | Push в feature-ветки | Нет | Нет |
| Reviewer | Review + approve MR | Нет | Нет |
| CI Publisher (SA) | Нет | Write to registry (write_registry) | Нет |
| Deploy Operator SA | Нет | read_registry (release images only) | Deploy (production, manual; Protected Environment) |   