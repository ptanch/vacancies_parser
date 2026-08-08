### Структура проекта

```
vacancies_parser/
│
├── .venv/                     # виртуальное окружение
├── .env                       # реальные секреты
├── .env.example               # шаблон без реальных значений
├── .gitignore                  
├── README.md                   
├── requirements.txt             
│
├── data/
│   └── vacancies.db            # SQLite база
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # точка входа, запускает всё асинхронно
│   ├── config.py                # чтение .env, все настройки
│   ├── models.py                 #[main.py](src/main.py) структура данных "вакансия" (dataclass)
│   ├── database.py               # работа с SQLite (aiosqlite)
│   │
│   └── parsers/
│       ├── __init__.py
│       ├── base.py               # общий интерфейс для всех парсеров
│       ├── hh_parser.py          # парсер hh.ru
│       └── telegram_parser.py    # парсер Telegram-каналов
│
└── tests/
    └── __init__.py               # тесты
```