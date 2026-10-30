# Learning Log — OpenAPI / Swagger (self-directed tool)

| # | Activity | Resource | Outcome / Problem faced |
|---|----------|----------|-------------------------|
| 1 | Read what OpenAPI is (spec vs. Swagger UI tool) | swagger.io "What is OpenAPI" | OpenAPI = machine-readable contract; Swagger UI = renderer of it |
| 2 | Generated first spec from FastAPI | FastAPI docs – "First Steps" | `/docs` and `/openapi.json` worked, but every endpoint sat under "default" |
| 3 | Grouped endpoints by module | FastAPI docs – "Metadata and Docs URLs" | Added `openapi_tags`; 5 tags = 5 modules |
| 4 | Added request examples | FastAPI docs – "Declare Request Example Data" | `Field(examples=[...])` makes "Try it out" usable without typing |
| 5 | Documented error responses | OpenAPI 3.1 spec – Responses Object | `responses={409: ...}` – 409/402 now visible in Swagger UI |
| 6 | Problem: 500 instead of 409 on double booking | Stack Overflow + FastAPI docs – "Handling Errors" | Mapped domain exceptions to status codes with exception handlers |
| 7 | Made the spec testable | own experiment | Contract test asserts every module tag and documented 409 exist |
| 8 | Exported spec for others | FastAPI `app.openapi()` | `docs/openapi.json` committed; can be imported into Postman |

**Alternative considered:** a hand-written Markdown API document / Postman collection.
Rejected because it drifts from the code; the OpenAPI spec is generated from the code and tested in CI.
