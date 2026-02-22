from django import forms

from .models import TYPE_LOCAL_CHOICES

DEPT_CHOICES = [
    ("01", "01 - Ain"),
    ("02", "02 - Aisne"),
    ("03", "03 - Allier"),
    ("04", "04 - Alpes-de-Haute-Provence"),
    ("05", "05 - Hautes-Alpes"),
    ("06", "06 - Alpes-Maritimes"),
    ("07", "07 - Ardèche"),
    ("08", "08 - Ardennes"),
    ("09", "09 - Ariège"),
    ("10", "10 - Aube"),
    ("11", "11 - Aude"),
    ("12", "12 - Aveyron"),
    ("13", "13 - Bouches-du-Rhône"),
    ("14", "14 - Calvados"),
    ("15", "15 - Cantal"),
    ("16", "16 - Charente"),
    ("17", "17 - Charente-Maritime"),
    ("18", "18 - Cher"),
    ("19", "19 - Corrèze"),
    ("2A", "2A - Corse-du-Sud"),
    ("2B", "2B - Haute-Corse"),
    ("21", "21 - Côte-d'Or"),
    ("22", "22 - Côtes-d'Armor"),
    ("23", "23 - Creuse"),
    ("24", "24 - Dordogne"),
    ("25", "25 - Doubs"),
    ("26", "26 - Drôme"),
    ("27", "27 - Eure"),
    ("28", "28 - Eure-et-Loir"),
    ("29", "29 - Finistère"),
    ("30", "30 - Gard"),
    ("31", "31 - Haute-Garonne"),
    ("32", "32 - Gers"),
    ("33", "33 - Gironde"),
    ("34", "34 - Hérault"),
    ("35", "35 - Ille-et-Vilaine"),
    ("36", "36 - Indre"),
    ("37", "37 - Indre-et-Loire"),
    ("38", "38 - Isère"),
    ("39", "39 - Jura"),
    ("40", "40 - Landes"),
    ("41", "41 - Loir-et-Cher"),
    ("42", "42 - Loire"),
    ("43", "43 - Haute-Loire"),
    ("44", "44 - Loire-Atlantique"),
    ("45", "45 - Loiret"),
    ("46", "46 - Lot"),
    ("47", "47 - Lot-et-Garonne"),
    ("48", "48 - Lozère"),
    ("49", "49 - Maine-et-Loire"),
    ("50", "50 - Manche"),
    ("51", "51 - Marne"),
    ("52", "52 - Haute-Marne"),
    ("53", "53 - Mayenne"),
    ("54", "54 - Meurthe-et-Moselle"),
    ("55", "55 - Meuse"),
    ("56", "56 - Morbihan"),
    ("57", "57 - Moselle"),
    ("58", "58 - Nièvre"),
    ("59", "59 - Nord"),
    ("60", "60 - Oise"),
    ("61", "61 - Orne"),
    ("62", "62 - Pas-de-Calais"),
    ("63", "63 - Puy-de-Dôme"),
    ("64", "64 - Pyrénées-Atlantiques"),
    ("65", "65 - Hautes-Pyrénées"),
    ("66", "66 - Pyrénées-Orientales"),
    ("67", "67 - Bas-Rhin"),
    ("68", "68 - Haut-Rhin"),
    ("69", "69 - Rhône"),
    ("70", "70 - Haute-Saône"),
    ("71", "71 - Saône-et-Loire"),
    ("72", "72 - Sarthe"),
    ("73", "73 - Savoie"),
    ("74", "74 - Haute-Savoie"),
    ("75", "75 - Paris"),
    ("76", "76 - Seine-Maritime"),
    ("77", "77 - Seine-et-Marne"),
    ("78", "78 - Yvelines"),
    ("79", "79 - Deux-Sèvres"),
    ("80", "80 - Somme"),
    ("81", "81 - Tarn"),
    ("82", "82 - Tarn-et-Garonne"),
    ("83", "83 - Var"),
    ("84", "84 - Vaucluse"),
    ("85", "85 - Vendée"),
    ("86", "86 - Vienne"),
    ("87", "87 - Haute-Vienne"),
    ("88", "88 - Vosges"),
    ("89", "89 - Yonne"),
    ("90", "90 - Territoire de Belfort"),
    ("91", "91 - Essonne"),
    ("92", "92 - Hauts-de-Seine"),
    ("93", "93 - Seine-Saint-Denis"),
    ("94", "94 - Val-de-Marne"),
    ("95", "95 - Val-d'Oise"),
    ("971", "971 - Guadeloupe"),
    ("972", "972 - Martinique"),
    ("973", "973 - Guyane"),
    ("974", "974 - La Réunion"),
    ("976", "976 - Mayotte"),
]


class PredictionForm(forms.Form):
    """
    C14/C17 - Formulaire de prédiction unique.
    Validation côté serveur complète.
    """

    type_local = forms.ChoiceField(
        choices=TYPE_LOCAL_CHOICES,
        label="Type de bien",
        widget=forms.Select(attrs={"aria-required": "true"}),
    )
    surface_reelle_bati = forms.FloatField(
        min_value=1,
        label="Surface bâtie (m²)",
        widget=forms.NumberInput(
            attrs={"placeholder": "ex: 75", "step": "0.5", "aria-required": "true"}
        ),
    )
    nombre_pieces_principales = forms.IntegerField(
        min_value=1,
        max_value=50,
        label="Nombre de pièces principales",
        widget=forms.NumberInput(attrs={"placeholder": "ex: 3", "aria-required": "true"}),
    )
    surface_terrain = forms.FloatField(
        min_value=0,
        required=False,
        label="Surface terrain (m²)",
        widget=forms.NumberInput(attrs={"placeholder": "ex: 200 (optionnel)", "step": "1"}),
    )
    code_departement = forms.ChoiceField(
        choices=DEPT_CHOICES,
        label="Département",
        widget=forms.Select(attrs={"aria-required": "true"}),
    )
    latitude = forms.FloatField(
        min_value=-90,
        max_value=90,
        label="Latitude",
        widget=forms.NumberInput(
            attrs={"placeholder": "ex: 48.8566", "step": "0.0001", "aria-required": "true"}
        ),
    )
    longitude = forms.FloatField(
        min_value=-180,
        max_value=180,
        label="Longitude",
        widget=forms.NumberInput(
            attrs={"placeholder": "ex: 2.3522", "step": "0.0001", "aria-required": "true"}
        ),
    )


class BatchUploadForm(forms.Form):
    """Formulaire upload CSV pour prédictions batch."""

    fichier_csv = forms.FileField(
        label="Fichier CSV",
        help_text="Format : surface_reelle_bati, nombre_pieces_principales, surface_terrain, longitude, latitude, type_local, code_departement",
        widget=forms.FileInput(attrs={"accept": ".csv", "aria-required": "true"}),
    )

    def clean_fichier_csv(self):
        f = self.cleaned_data["fichier_csv"]
        if not f.name.endswith(".csv"):
            raise forms.ValidationError("Seuls les fichiers .csv sont acceptés.")
        if f.size > 5 * 1024 * 1024:  # 5 Mo max
            raise forms.ValidationError("Le fichier ne doit pas dépasser 5 Mo.")
        return f


class PredictionFilterForm(forms.Form):
    """Filtres pour l'historique des prédictions."""

    type_local = forms.ChoiceField(
        choices=[("", "Tous les types")] + TYPE_LOCAL_CHOICES, required=False, label="Type de bien"
    )
    code_departement = forms.CharField(
        required=False,
        max_length=3,
        label="Département",
        widget=forms.TextInput(attrs={"placeholder": "ex: 75"}),
    )
    date_debut = forms.DateField(
        required=False, label="Du", widget=forms.DateInput(attrs={"type": "date"})
    )
    date_fin = forms.DateField(
        required=False, label="Au", widget=forms.DateInput(attrs={"type": "date"})
    )
