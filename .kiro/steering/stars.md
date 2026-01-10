---
inclusion: always
---
Отлично! Теперь у меня есть вся необходимая документация. Вот ключевые моменты для интеграции Telegram Stars:

Ключевые моменты из документации:
1. Создание Invoice (Bot API)
Используем метод createInvoiceLink для создания ссылки на инвойс
Валюта должна быть XTR (Telegram Stars)
provider_token оставляем пустым для цифровых товаров
2. Открытие Invoice в Mini App
Используем Telegram.WebApp.openInvoice(url, callback)
Событие invoiceClosed возвращает статус: paid, cancelled, failed, pending
3. Обработка платежа (Bot)
Бот получает pre_checkout_query - нужно ответить через answerPrecheckoutQuery
После успешной оплаты приходит successful_payment
4. Архитектура для продакшена:
Mini App (Next.js) → API Route → Bot API (createInvoiceLink)
                                      ↓
User pays → Bot receives pre_checkout_query → answerPrecheckoutQuery
                                      ↓
                    successful_payment → Update leaderboard
Хочешь, чтобы я начал реализацию? Нужно будет:

API Route в Next.js (/api/create-invoice) - создаёт invoice link через Bot API
Обновить DonationPage - вызывает openInvoice вместо мока
Добавить обработчики в бота - pre_checkout_query и successful_payment
Создать систему хранения донатов - для лидерборда