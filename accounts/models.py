from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    consentement_rgpd = models.BooleanField(
        default=False, help_text="L'utilisateur a accepté la politique de confidentialité."
    )
    consentement_date = models.DateTimeField(null=True, blank=True)
    demande_suppression = models.BooleanField(default=False)
    demande_suppression_date = models.DateTimeField(null=True, blank=True)

    # ↓ Ces deux lignes corrigent l'erreur
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="accounts_user_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="accounts_user_set",
        blank=True,
    )

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.username

    @property
    def nb_predictions(self):
        return self.predictions.count()
