from django.contrib import admin
from .models import Prediction, PredictionBatch


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_local', 'surface_reelle_bati', 'code_departement', 'prix_estime', 'status', 'created_at')
    list_filter = ('status', 'type_local')
    search_fields = ('user__username', 'code_departement')


@admin.register(PredictionBatch)
class PredictionBatchAdmin(admin.ModelAdmin):
    list_display = ('user', 'nb_lignes', 'nb_succes', 'status', 'created_at')
    list_filter = ('status',)
