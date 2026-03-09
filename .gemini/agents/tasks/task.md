@orchestrator фикси эти штуки, планируй и делегируй агентам: GET
	https://m.wifiobd.ru/api/v1/delivery/orders/7535996a-8480-4970-a5fd-c487f80dce53/c2c-shipment
Состояние
400
Bad Request
ВерсияHTTP/1.1
Передано195 б (размер 42 б)
Referrer policystrict-origin-when-cross-origin
Поиск в DNSDNS через HTTPS
detail	"Provider is not C2C (ozon/wb)"
как импортируется, если не найдено? GET
	https://m.wifiobd.ru/media/products/0c26ca37_module_logger.png
Состояние
404
Not Found
ВерсияHTTP/1.1
Передано210 б (размер 22 б)
Referrer policystrict-origin-when-cross-origin
Приоритет запросаLowest
Поиск в DNSDNS через HTTPS GET
	https://m.wifiobd.ru/media/products/0c26ca37_module_logger.png
Состояние
404
Not Found
ВерсияHTTP/1.1
Передано210 б (размер 22 б)
Referrer policystrict-origin-when-cross-origin
Приоритет запросаLowest
Поиск в DNSDNS через HTTPS

 File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
sb_backend      |     await route.handle(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 119, in app
sb_backend      |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 105, in app
sb_backend      |     response = await f(request)
sb_backend      |                ^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 425, in app
sb_backend      |     raw_response = await run_endpoint_function(
sb_backend      |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 313, in run_endpoint_function
sb_backend      |     return await dependant.call(**values)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 551, in list_users
sb_backend      |     "items": [UserResponse.model_validate(u) for u in users],
sb_backend      |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/pydantic/main.py", line 627, in model_validate
sb_backend      |     return cls.__pydantic_validator__.validate_python(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserResponse
sb_backend      | email
sb_backend      |   value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
sb_backend      | 77.239.239.99:0 - "GET /api/v1/admin/users?skip=0&limit=20&q=%D0%BE%D0%BB%D0%B5%D0%B3 HTTP/1.1" 500
sb_backend      | [2026-03-09 08:16:25 +0000] [7] [ERROR] Exception in ASGI application
sb_backend      | Traceback (most recent call last):
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 416, in run_asgi
sb_backend      |     result = await app(  # type: ignore[func-returns-value]
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/applications.py", line 1134, in __call__
sb_backend      |     await super().__call__(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/applications.py", line 107, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
sb_backend      |     await self.app(scope, receive, _send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 87, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
sb_backend      |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 716, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
sb_backend      |     await route.handle(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 119, in app
sb_backend      |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 105, in app
sb_backend      |     response = await f(request)
sb_backend      |                ^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 425, in app
sb_backend      |     raw_response = await run_endpoint_function(
sb_backend      |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 313, in run_endpoint_function
sb_backend      |     return await dependant.call(**values)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 551, in list_users
sb_backend      |     "items": [UserResponse.model_validate(u) for u in users],
sb_backend      |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/pydantic/main.py", line 627, in model_validate
sb_backend      |     return cls.__pydantic_validator__.validate_python(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserResponse
sb_backend      | email
sb_backend      |   value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
sb_backend      | 77.239.239.99:0 - "GET /api/v1/admin/users?skip=0&limit=20&q=%D0%BE%D0%BB%D0%B5%D0%B3 HTTP/1.1" 500
sb_backend      | [2026-03-09 08:16:25 +0000] [8] [ERROR] Exception in ASGI application
sb_backend      | Traceback (most recent call last):
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 416, in run_asgi
sb_backend      |     result = await app(  # type: ignore[func-returns-value]
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/applications.py", line 1134, in __call__
sb_backend      |     await super().__call__(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/applications.py", line 107, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
sb_backend      |     await self.app(scope, receive, _send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 87, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
sb_backend      |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 716, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
sb_backend      |     await route.handle(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 119, in app
sb_backend      |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 105, in app
sb_backend      |     response = await f(request)
sb_backend      |                ^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 425, in app
sb_backend      |     raw_response = await run_endpoint_function(
sb_backend      |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 313, in run_endpoint_function
sb_backend      |     return await dependant.call(**values)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 551, in list_users
sb_backend      |     "items": [UserResponse.model_validate(u) for u in users],
sb_backend      |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/pydantic/main.py", line 627, in model_validate
sb_backend      |     return cls.__pydantic_validator__.validate_python(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserResponse
sb_backend      | email
sb_backend      |   value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
sb_backend      | 172.27.0.6:0 - "GET /api/v1/products?per_page=4 HTTP/1.1" 200
sb_backend      | 172.27.0.6:0 - "GET /api/v1/blog/posts?per_page=3 HTTP/1.1" 200
sb_backend      | 77.239.239.99:0 - "GET /api/v1/admin/users?skip=0&limit=20&q=%D0%BE%D0%BB%D0%B5 HTTP/1.1" 500
sb_backend      | [2026-03-09 08:16:30 +0000] [8] [ERROR] Exception in ASGI application
sb_backend      | Traceback (most recent call last):
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 416, in run_asgi
sb_backend      |     result = await app(  # type: ignore[func-returns-value]
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/applications.py", line 1134, in __call__
sb_backend      |     await super().__call__(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/applications.py", line 107, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
sb_backend      |     await self.app(scope, receive, _send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 87, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
sb_backend      |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 716, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
sb_backend      |     await route.handle(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 119, in app
sb_backend      |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 105, in app
sb_backend      |     response = await f(request)
sb_backend      |                ^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 425, in app
sb_backend      |     raw_response = await run_endpoint_function(
sb_backend      |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 313, in run_endpoint_function
sb_backend      |     return await dependant.call(**values)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 551, in list_users
sb_backend      |     "items": [UserResponse.model_validate(u) for u in users],
sb_backend      |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/pydantic/main.py", line 627, in model_validate
sb_backend      |     return cls.__pydantic_validator__.validate_python(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserResponse
sb_backend      | email
sb_backend      |   value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
sb_backend      | 77.239.239.99:0 - "GET /api/v1/admin/users?skip=0&limit=20&q=%D0%BE%D0%BB%D0%B5 HTTP/1.1" 500
sb_backend      | [2026-03-09 08:16:30 +0000] [7] [ERROR] Exception in ASGI application
sb_backend      | Traceback (most recent call last):
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 416, in run_asgi
sb_backend      |     result = await app(  # type: ignore[func-returns-value]
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/applications.py", line 1134, in __call__
sb_backend      |     await super().__call__(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/applications.py", line 107, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
sb_backend      |     await self.app(scope, receive, _send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 87, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
sb_backend      |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 716, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
sb_backend      |     await route.handle(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 119, in app
sb_backend      |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 105, in app
sb_backend      |     response = await f(request)
sb_backend      |                ^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 425, in app
sb_backend      |     raw_response = await run_endpoint_function(
sb_backend      |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 313, in run_endpoint_function
sb_backend      |     return await dependant.call(**values)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 551, in list_users
sb_backend      |     "items": [UserResponse.model_validate(u) for u in users],
sb_backend      |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/pydantic/main.py", line 627, in model_validate
sb_backend      |     return cls.__pydantic_validator__.validate_python(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserResponse
sb_backend      | email
sb_backend      |   value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
sb_backend      | 77.239.239.99:0 - "GET /api/v1/admin/users?skip=0&limit=20&q=%D0%BE%D0%BB%D0%B5 HTTP/1.1" 500
sb_backend      | [2026-03-09 08:16:30 +0000] [9] [ERROR] Exception in ASGI application
sb_backend      | Traceback (most recent call last):
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 416, in run_asgi
sb_backend      |     result = await app(  # type: ignore[func-returns-value]
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/applications.py", line 1134, in __call__
sb_backend      |     await super().__call__(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/applications.py", line 107, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
sb_backend      |     await self.app(scope, receive, _send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 87, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
sb_backend      |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 716, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
sb_backend      |     await route.handle(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 119, in app
sb_backend      |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 105, in app
sb_backend      |     response = await f(request)
sb_backend      |                ^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 425, in app
sb_backend      |     raw_response = await run_endpoint_function(
sb_backend      |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 313, in run_endpoint_function
sb_backend      |     return await dependant.call(**values)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 551, in list_users
sb_backend      |     "items": [UserResponse.model_validate(u) for u in users],
sb_backend      |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/pydantic/main.py", line 627, in model_validate
sb_backend      |     return cls.__pydantic_validator__.validate_python(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserResponse
sb_backend      | email
sb_backend      |   value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
sb_backend      | 77.239.239.99:0 - "GET /api/v1/admin/users?skip=0&limit=20&q=%D0%BE%D0%BB%D0%B5 HTTP/1.1" 500
sb_backend      | [2026-03-09 08:16:30 +0000] [7] [ERROR] Exception in ASGI application
sb_backend      | Traceback (most recent call last):
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 416, in run_asgi
sb_backend      |     result = await app(  # type: ignore[func-returns-value]
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/applications.py", line 1134, in __call__
sb_backend      |     await super().__call__(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/applications.py", line 107, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
sb_backend      |     await self.app(scope, receive, _send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 87, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
sb_backend      |     return await self.app(scope, receive, send)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
sb_backend      |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 716, in __call__
sb_backend      |     await self.middleware_stack(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
sb_backend      |     await route.handle(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
sb_backend      |     await self.app(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 119, in app
sb_backend      |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
sb_backend      |     raise exc
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
sb_backend      |     await app(scope, receive, sender)
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 105, in app
sb_backend      |     response = await f(request)
sb_backend      |                ^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 425, in app
sb_backend      |     raw_response = await run_endpoint_function(
sb_backend      |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 313, in run_endpoint_function
sb_backend      |     return await dependant.call(**values)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 551, in list_users
sb_backend      |     "items": [UserResponse.model_validate(u) for u in users],
sb_backend      |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/pydantic/main.py", line 627, in model_validate
sb_backend      |     return cls.__pydantic_validator__.validate_python(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      | pydantic_core._pydantic_core.ValidationError: 1 validation error for UserResponse
sb_backend      | email
sb_backend      |   value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
sb_meilisearch  | 2026-03-09T08:16:34.570069Z  INFO HTTP request{method=GET host="localhost:7700" route=/health query_parameters= user_agent=curl/8.14.1 status_code=200}: meilisearch: close time.busy=212µs time.idle=37.6µs