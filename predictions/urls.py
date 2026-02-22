from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("prediction/nouveau/", views.predict, name="predict"),
    path("prediction/<int:pk>/", views.prediction_detail, name="prediction_detail"),
    path("prediction/<int:pk>/supprimer/", views.prediction_delete, name="prediction_delete"),
    path("historique/", views.prediction_history, name="prediction_history"),
    path("batch/", views.batch_upload, name="batch_upload"),
    path("batch/<int:pk>/", views.batch_detail, name="batch_detail"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("export/json/", views.export_json, name="export_json"),
    path("api/health/", views.api_health, name="api_health"),
]
