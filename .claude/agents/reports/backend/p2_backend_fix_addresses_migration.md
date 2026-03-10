## Status: DONE

## Completed:
- Добавлено детальное логирование в migrate_addresses (строки 693-862)
- Добавлено детальное логирование в migrate_devices (уже было, улучшено)
- Добавлены счётчики в extra_data для addresses: addresses_no_customer, addresses_no_user, addresses_duplicate
- Добавлены счётчики в extra_data для devices: devices_no_customer, devices_no_user, devices_duplicate
- Добавлено логирование общего количества записей в oc_address (аналогично devices)
- Логируется email_preview и email_hash_prefix при каждом skip для отладки
- Курсор addresses_last_id корректно обновляется даже при skip (было корректно, проверено)

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/admin/migration_service.py

## Changes Made:

### migrate_addresses (строки 679-862):
1. Добавлено логирование старта миграции с job_id и cursor
2. Добавлен подсчёт total_in_oc_addresses (SELECT COUNT(*) FROM oc_address)
3. Добавлено логирование fetched batch size
4. Добавлены счётчики: skipped_duplicate, skipped_no_customer, skipped_no_user
5. Логирование каждой строки: oc_address_id, oc_customer_id
6. При skip duplicate: logger.info с причиной "already_migrated"
7. При отсутствии customer: logger.warning с oc_customer_id и причиной
8. При найденном customer: логируется email_preview (первые 3 символа + ***) и флаг email_empty
9. Логируется email_hash_prefix (первые 8 символов) для отладки
10. При отсутствии user: logger.warning с email_hash_prefix, email_preview и причиной "user_not_found_by_email_hash_in_new_db"
11. При найденном user: логируется user_id
12. В metadata добавлены: addresses_no_customer, addresses_no_user, addresses_duplicate
13. В финальном логе migrate_addresses_batch выводятся все счётчики

### migrate_devices (строки 863-1083):
1. Добавлены счётчики: skipped_no_customer, skipped_no_user, skipped_duplicate (уже было детальное логирование)
2. Исправлены инкременты skipped — теперь происходят ДО logger.warning (было после)
3. В metadata добавлены: devices_no_customer, devices_no_user, devices_duplicate
4. В финальном логе migrate_devices_batch выводятся все счётчики

## Root Cause Analysis:
Проблема была в отсутствии детального логирования. Теперь при каждом skip будет видно:
- Какой именно oc_address_id/oc_device_id пропущен
- На каком этапе (duplicate / no_customer / no_user)
- Email пользователя (первые 3 символа) для сопоставления с таблицей users
- Email_hash_prefix для проверки корректности хеширования

Это позволит понять, почему адреса/устройства не находят своих владельцев:
- Если skipped_no_customer > 0 — проблема в oc_customer (записи удалены или не существуют)
- Если skipped_no_user > 0 — пользователи не мигрированы или email_hash не совпадает

## Contracts Verified:
- Pydantic schemas: N/A (только логирование)
- DI via Depends: ✅
- No Any: ✅
- ruff: ✅ (All checks passed!)
- mypy: ✅ (Success: no issues found)
- pytest: ⏭️ (не запускался по требованию задачи)

## Next Steps:
1. Запустить миграцию addresses и проверить логи — теперь будет видно точную причину skip
2. Если skipped_no_user > 0 — проверить, все ли пользователи из oc_customer мигрированы в users
3. Сравнить email_hash из логов addresses с email_hash в таблице users
4. Если пользователи с пустыми email были пропущены — решить, создавать ли для них записи или оставить адреса несвязанными

## Blockers:
- none

## Notes:
- НЕ запускал pytest по требованию задачи
- Курсор addresses_last_id обновляется корректно (строка 712: current_last_id = oc_addr.address_id)
- Все изменения — только добавление логирования, бизнес-логика не изменена
