from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


TYPE_LOCAL_CHOICES = [
    ('Appartement', 'Appartement'),
    ('Maison', 'Maison'),
    ('Dépendance', 'Dépendance'),
    ('Local industriel. commercial ou assimilé', 'Local commercial/industriel'),
]


class Prediction(models.Model):
    """
    C14/C17 - Enregistrement d'une prédiction individuelle.
    Conserve les inputs et outputs pour historique et audit.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions',
        verbose_name="Utilisateur"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de prédiction")

    # ─── Données d'entrée ───────────────────────────────────────────────────
    surface_reelle_bati = models.FloatField(
        validators=[MinValueValidator(1.0)],
        verbose_name="Surface bâtie (m²)"
    )
    nombre_pieces_principales = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Nombre de pièces"
    )
    surface_terrain = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Surface terrain (m²)"
    )
    longitude = models.FloatField(verbose_name="Longitude")
    latitude = models.FloatField(verbose_name="Latitude")
    type_local = models.CharField(max_length=50, choices=TYPE_LOCAL_CHOICES, verbose_name="Type de bien")
    code_departement = models.CharField(max_length=3, verbose_name="Département")

    # ─── Résultats ──────────────────────────────────────────────────────────
    prix_estime = models.FloatField(null=True, blank=True, verbose_name="Prix estimé (€)")
    intervalle_bas = models.FloatField(null=True, blank=True, verbose_name="Borne basse (€)")
    intervalle_haut = models.FloatField(null=True, blank=True, verbose_name="Borne haute (€)")
    prix_m2 = models.FloatField(null=True, blank=True, verbose_name="Prix au m² (€)")
    modele_version = models.CharField(max_length=100, blank=True, verbose_name="Version du modèle")
    latence_api_ms = models.FloatField(null=True, blank=True, verbose_name="Latence API (ms)")

    # ─── Statut ─────────────────────────────────────────────────────────────
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('success', 'Succès'),
        ('error', 'Erreur'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Prédiction"
        verbose_name_plural = "Prédictions"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.user.username}] {self.type_local} {self.surface_reelle_bati}m² - {self.created_at.date()}"

    @property
    def input_data(self):
        return {
            'surface_reelle_bati': self.surface_reelle_bati,
            'nombre_pieces_principales': self.nombre_pieces_principales,
            'surface_terrain': self.surface_terrain,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'type_local': self.type_local,
            'code_departement': self.code_departement,
        }


class PredictionBatch(models.Model):
    """
    C17 - Traitement en lot via upload CSV.
    Consomme /predict/batch de l'API externe.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='batches',
        verbose_name="Utilisateur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    fichier_csv = models.FileField(upload_to='batches/', verbose_name="Fichier CSV")
    nb_lignes = models.IntegerField(default=0)
    nb_succes = models.IntegerField(default=0)
    nb_erreurs = models.IntegerField(default=0)

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('done', 'Terminé'),
        ('error', 'Erreur'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Batch de prédictions"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.user.username}] Batch {self.id} - {self.status}"
