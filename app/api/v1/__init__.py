"""
API v1 endpoints initialization.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    accounts,
    transactions,
    auth,
    transfers,
    cards,
    admin_errors,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(accounts.router)
router.include_router(transactions.router)
router.include_router(transfers.router)
router.include_router(cards.router)
router.include_router(admin_errors.router)
