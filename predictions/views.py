import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BatchUploadForm, PredictionFilterForm, PredictionForm
from .models import Prediction, PredictionBatch
from .services.prediction_service import create_prediction, process_batch_from_csv
from .services.report_service import export_predictions_csv, export_predictions_json

logger = logging.getLogger("predictions")


@login_required
def dashboard(request):
    uid = request.user.pk
    qs = Prediction.objects.filter(user_id=uid, status="success")
    stats = qs.aggregate(
        total=Count("id"),
        prix_moyen=Avg("prix_estime"),
        prix_min=Min("prix_estime"),
        prix_max=Max("prix_estime"),
    )
    recent = qs[:5]
    return render(
        request,
        "predictions/dashboard.html",
        {
            "stats": stats,
            "recent": recent,
        },
    )


@login_required
def predict(request):
    if request.method == "POST":
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction = create_prediction(request.user, form.cleaned_data)
            if prediction.status == "success":
                messages.success(
                    request, f"Prédiction effectuée : {prediction.prix_estime:,.0f} €"
                )
                return redirect("prediction_detail", pk=prediction.pk)
            else:
                messages.error(
                    request, f"Erreur lors de la prédiction : {prediction.error_message}"
                )
    else:
        form = PredictionForm()
    return render(request, "predictions/predict.html", {"form": form})


@login_required
def prediction_detail(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk, user_id=request.user.pk)
    return render(request, "predictions/prediction_detail.html", {"prediction": prediction})


@login_required
def prediction_history(request):
    qs = Prediction.objects.filter(user_id=request.user.pk)
    form = PredictionFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get("type_local"):
            qs = qs.filter(type_local=form.cleaned_data["type_local"])
        if form.cleaned_data.get("code_departement"):
            qs = qs.filter(code_departement=form.cleaned_data["code_departement"])
        if form.cleaned_data.get("date_debut"):
            qs = qs.filter(created_at__date__gte=form.cleaned_data["date_debut"])
        if form.cleaned_data.get("date_fin"):
            qs = qs.filter(created_at__date__lte=form.cleaned_data["date_fin"])
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "predictions/history.html",
        {
            "page_obj": page_obj,
            "filter_form": form,
        },
    )


@login_required
def prediction_delete(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk, user_id=request.user.pk)
    if request.method == "POST":
        prediction.delete()
        messages.success(request, "Prédiction supprimée.")
        return redirect("prediction_history")
    return render(request, "predictions/confirm_delete.html", {"prediction": prediction})


@login_required
def batch_upload(request):
    if request.method == "POST":
        form = BatchUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["fichier_csv"]
            csv_file.seek(0)  # ← remet le curseur au début
            content = csv_file.read()
            csv_file.seek(0)  # ← remet à zéro pour la sauvegarde

            batch = PredictionBatch.objects.create(
                user_id=request.user.pk,
                fichier_csv=csv_file,
            )
            batch = process_batch_from_csv(request.user, batch, content)
            if batch.status == "done":
                messages.success(
                    request,
                    f"Batch traité : {batch.nb_succes}/{batch.nb_lignes} prédictions réussies.",
                )
            else:
                messages.error(request, f"Erreur batch : {batch.error_message}")
            return redirect("batch_detail", pk=batch.pk)
    else:
        form = BatchUploadForm()
    return render(request, "predictions/batch_upload.html", {"form": form})


@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(PredictionBatch, pk=pk, user_id=request.user.pk)
    return render(request, "predictions/batch_detail.html", {"batch": batch})


@login_required
def export_csv(request):
    qs = Prediction.objects.filter(user_id=request.user.pk)
    content = export_predictions_csv(qs)
    response = HttpResponse(content, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="predictions_immobilier.csv"'
    return response


@login_required
def export_json(request):
    qs = Prediction.objects.filter(user_id=request.user.pk)
    content = export_predictions_json(qs)
    response = HttpResponse(content, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="predictions_immobilier.json"'
    return response


@login_required
def api_health(request):
    from .services import APIClientError, api_client

    try:
        status = api_client.health()
        return JsonResponse({"status": "ok", "api": status})
    except APIClientError as e:
        return JsonResponse({"status": "error", "detail": str(e)}, status=503)
