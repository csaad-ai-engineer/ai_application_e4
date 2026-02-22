"""
tests/test_forms.py

C18 — Tests unitaires des formulaires Django.
"""

from django.test import TestCase

from predictions.forms import PredictionForm


class TestPredictionForm(TestCase):

    def _valid_data(self, **kwargs):
        base = {
            "type_local": "Appartement",
            "surface_reelle_bati": 75.0,
            "nombre_pieces_principales": 3,
            "surface_terrain": None,
            "code_departement": "75",
            "latitude": 48.8566,
            "longitude": 2.3522,
        }
        base.update(kwargs)
        return base

    def test_valid_form(self):
        form = PredictionForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_missing_required_field(self):
        data = self._valid_data()
        del data["surface_reelle_bati"]
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert "surface_reelle_bati" in form.errors

    def test_negative_surface_invalid(self):
        form = PredictionForm(data=self._valid_data(surface_reelle_bati=-10))
        assert not form.is_valid()
        assert "surface_reelle_bati" in form.errors

    def test_zero_pieces_invalid(self):
        form = PredictionForm(data=self._valid_data(nombre_pieces_principales=0))
        assert not form.is_valid()

    def test_latitude_out_of_range(self):
        form = PredictionForm(data=self._valid_data(latitude=100))
        assert not form.is_valid()

    def test_longitude_out_of_range(self):
        form = PredictionForm(data=self._valid_data(longitude=-200))
        assert not form.is_valid()

    def test_surface_terrain_optional(self):
        data = self._valid_data()
        data["surface_terrain"] = ""
        form = PredictionForm(data=data)
        assert form.is_valid()
