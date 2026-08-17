import uuid
import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        
        # Attach to request state
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Inject headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = trace_id
            
            process_time = time.time() - start_time
            logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Latency: {process_time:.4f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(f"Unhandled exception during {request.method} {request.url.path}: {e}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                    "request_id": request_id,
                    "trace_id": trace_id
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Trace-ID": trace_id
                }
            )
