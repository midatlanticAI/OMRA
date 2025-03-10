"""
API package for the OpenManus Appliance Repair Business Automation System.
"""
from fastapi import APIRouter

from backend.api.customers import router as customers_router
from backend.api.service_requests import router as service_requests_router
from backend.api.integrations import router as integrations_router
from backend.api.documents import router as documents_router
from backend.api.agents import router as agents_router
from backend.api.auth import router as auth_router

# Create main API router
api_router = APIRouter()

# Register routers
api_router.include_router(auth_router)
api_router.include_router(customers_router)
api_router.include_router(service_requests_router)
api_router.include_router(integrations_router)
api_router.include_router(documents_router)
api_router.include_router(agents_router)

# Additional routers can be registered here
# api_router.include_router(appointments_router)
# api_router.include_router(invoices_router)
# api_router.include_router(reports_router)
# etc. 