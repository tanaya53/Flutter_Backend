from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InventoryItemViewSet,
    InventoryTransactionViewSet,
    IssueStockView,
    ReturnStockView,
    InventorySummaryView
)

router = DefaultRouter()
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transactions')
router.register(r'', InventoryItemViewSet, basename='inventory-items')

urlpatterns = [
    path('issue/', IssueStockView.as_view(), name='inventory-issue'),
    path('return/', ReturnStockView.as_view(), name='inventory-return'),
    path('summary/', InventorySummaryView.as_view(), name='inventory-summary'),
    path('', include(router.urls)),
]
