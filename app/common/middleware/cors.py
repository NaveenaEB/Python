from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle Preflight (OPTIONS) requests
        if request.method == "OPTIONS":
            response = Response()
        else:
            # Process the actual request
            response = await call_next(request)

        # Define allowed origins (In production, load these from environment variables)
        allowed_origins = ["http://localhost:3000", "http://localhost"]
        origin = request.headers.get("Origin")

        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Expose-Headers"] = "Content-Length, Content-Range"

        return response