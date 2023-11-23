import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.auth_exceptions import AuthException
from app.viewmodels.api_response import APIResponse

logger = logging.getLogger(__name__)

def setup_exacption_handler(app: FastAPI):
    
    
    @app.exception_handler(AuthException)
    def handle_auth_exception(_, e: AuthException):
        e_message = e.detail
        logger.warning("Some error occurred during authentication/authorization: %s", e_message, exc_info=e)
        api_response = APIResponse(status_code=e.status_code, message = e_message)
        return JSONResponse(api_response.to_dict(), status_code=api_response.status_code)
    
    
    @app.exception_handler(HTTPException)
    def handle_http_exception(request: Request, e: HTTPException):
        e_message = e.detail
        logger.exception("Something bad happend during request %s: %s", request.url, e_message, exc_info=e)
        api_response = APIResponse(status_code=e.status_code, message=e_message)
        return JSONResponse(api_response.to_dict(), status_code=api_response.status_code)
        
    
    @app.exception_handler(Exception)
    def handle_exception(_, e: Exception):
        logger.exception("Some Error occurred: %s", e, exc_info=e)
        api_response = APIResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Internal Error")
        return JSONResponse(api_response.to_dict(), status_code=api_response.status_code)
    
    