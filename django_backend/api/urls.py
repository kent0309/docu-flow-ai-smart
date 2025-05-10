
from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.DocumentListCreateView.as_view(), name='document-list-create'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/summarize/', views.SummarizeDocumentView.as_view(), name='document-summarize'),
    path('documents/<int:pk>/extract/', views.ExtractDataView.as_view(), name='document-extract'),
    path('processed-documents/', views.ProcessedDocumentListView.as_view(), name='processed-document-list'),
    path('processed-documents/<int:pk>/', views.ProcessedDocumentDetailView.as_view(), name='processed-document-detail'),
]
