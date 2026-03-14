@orchestrator fix delegateion for this ^^^^
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
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 960, in list_devices
sb_backend      |     result = await session.execute(items_stmt)
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/session.py", line 449, in execute
sb_backend      |     result = await greenlet_spawn(
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 203, in greenlet_spawn
sb_backend      |     result = context.switch(value)
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2351, in execute
sb_backend      |     return self._execute_internal(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2249, in _execute_internal
sb_backend      |     result: Result[Any] = compile_state_cls.orm_execute_statement(
sb_backend      |                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/context.py", line 309, in orm_execute_statement
sb_backend      |     return cls.orm_setup_cursor_result(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/context.py", line 616, in orm_setup_cursor_result
sb_backend      |     return loading.instances(result, querycontext)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/loading.py", line 262, in instances
sb_backend      |     _prebuffered = list(chunks(None))
sb_backend      |                    ^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/loading.py", line 220, in chunks
sb_backend      |     fetch = cursor._raw_all_rows()
sb_backend      |             ^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/engine/result.py", line 541, in _raw_all_rows
sb_backend      |     return [make_row(row) for row in rows]
sb_backend      |             ^^^^^^^^^^^^^
sb_backend      |   File "lib/sqlalchemy/cyextension/resultproxy.pyx", line 22, in sqlalchemy.cyextension.resultproxy.BaseRow.__init__
sb_backend      |   File "lib/sqlalchemy/cyextension/resultproxy.pyx", line 79, in sqlalchemy.cyextension.resultproxy._apply_processors
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/sql/sqltypes.py", line 1829, in process
sb_backend      |     value = self._object_value_for_elem(value)
sb_backend      |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/sql/sqltypes.py", line 1711, in _object_value_for_elem
sb_backend      |     raise LookupError(
sb_backend      | LookupError: 'wifi_obd2' is not among the defined enum values. Enum name: devicemodel. Possible values: WIFI_OBD2, WIFI_OBD2_A..
sb_backend      | 77.239.239.99:0 - "GET /api/v1/admin/devices?page=1&per_page=50 HTTP/1.1" 500
sb_backend      | [2026-03-14 08:59:30 +0000] [7] [ERROR] Exception in ASGI application
sb_backend      | Traceback (most recent call last):
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/sql/sqltypes.py", line 1709, in _object_value_for_elem
sb_backend      |     return self._object_lookup[elem]  # type: ignore[return-value]
sb_backend      |            ~~~~~~~~~~~~~~~~~~~^^^^^^
sb_backend      | KeyError: 'wifi_obd2'
sb_backend      |
sb_backend      | The above exception was the direct cause of the following exception:
sb_backend      |
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
sb_backend      |   File "/app/app/api/v1/admin/router.py", line 960, in list_devices
sb_backend      |     result = await session.execute(items_stmt)
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/session.py", line 449, in execute
sb_backend      |     result = await greenlet_spawn(
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 203, in greenlet_spawn
sb_backend      |     result = context.switch(value)
sb_backend      |              ^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2351, in execute
sb_backend      |     return self._execute_internal(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2249, in _execute_internal
sb_backend      |     result: Result[Any] = compile_state_cls.orm_execute_statement(
sb_backend      |                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/context.py", line 309, in orm_execute_statement
sb_backend      |     return cls.orm_setup_cursor_result(
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/context.py", line 616, in orm_setup_cursor_result
sb_backend      |     return loading.instances(result, querycontext)
sb_backend      |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/loading.py", line 262, in instances
sb_backend      |     _prebuffered = list(chunks(None))
sb_backend      |                    ^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/orm/loading.py", line 220, in chunks
sb_backend      |     fetch = cursor._raw_all_rows()
sb_backend      |             ^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/engine/result.py", line 541, in _raw_all_rows
sb_backend      |     return [make_row(row) for row in rows]
sb_backend      |             ^^^^^^^^^^^^^
sb_backend      |   File "lib/sqlalchemy/cyextension/resultproxy.pyx", line 22, in sqlalchemy.cyextension.resultproxy.BaseRow.__init__
sb_backend      |   File "lib/sqlalchemy/cyextension/resultproxy.pyx", line 79, in sqlalchemy.cyextension.resultproxy._apply_processors
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/sql/sqltypes.py", line 1829, in process
sb_backend      |     value = self._object_value_for_elem(value)
sb_backend      |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sb_backend      |   File "/usr/local/lib/python3.12/site-packages/sqlalchemy/sql/sqltypes.py", line 1711, in _object_value_for_elem
sb_backend      |     raise LookupError(
sb_backend      | LookupError: 'wifi_obd2' is not among the defined enum values. Enum name: devicemodel. Possible values: WIFI_OBD2, WIFI_OBD2_A..
sb_meilisearch  | 2026-03-14T08:59:32.178672Z  INFO HTTP request{method=GET host="localhost:7700" route=/health query_parameters= user_agent=curl/8.14.1 status_code=200}: meilisearch: close time.busy=151µs time.idle=24.2µs