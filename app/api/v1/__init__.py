"""
API v1 endpoints initialization.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import accounts, transactions, auth, transfers

router = APIRouter()

router.include_router(auth.router)
router.include_router(accounts.router)
router.include_router(transactions.router)
router.include_router(transfers.router)
