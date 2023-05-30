from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

# Create your views here.


def search_income(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")
        income = (
            UserIncome.objects.filter(
                amount__istartswith=search_str, owner=request.user
            )
            | UserIncome.objects.filter(
                date__istartswith=search_str, owner=request.user
            )
            | UserIncome.objects.filter(
                description__icontains=search_str, owner=request.user
            )
            | UserIncome.objects.filter(
                source__icontains=search_str, owner=request.user
            )
        )
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url="/authentication/login")
def index(request):
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get("page")
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except UserPreference.DoesNotExist:
        currency = "USD - United States Dollar"

    context = {
        "income": income,
        "page_obj": page_obj,
        "currency": currency,
    }
    return render(request, "income/index.html", context)


@login_required(login_url="/authentication/login")
def add_income(request):
    sources = Source.objects.all()
    context = {"sources": sources, "values": request.POST}

    if request.method == "GET":
        return render(request, "income/add-income.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "income/add-income.html", context)

        description = request.POST["description"]
        date = request.POST["income_date"]
        source = request.POST["source"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "income/add-income.html", context)

        UserIncome.objects.create(
            amount=amount,
            date=date,
            description=description,
            source=source,
            owner=request.user,
        )
        messages.success(request, "Record saved successfully")

        return redirect("income")


def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {"income": income, "values": income, "sources": sources}
    if request.method == "GET":
        return render(request, "income/edit-income.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "income/edit-income.html", context)

        description = request.POST["description"]
        date = request.POST["income_date"]
        source = request.POST["source"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "income/edit-income.html", context)

        income.amount = amount
        income.date = date
        income.description = description
        income.source = source

        income.save()

        messages.success(request, "Record Updated successfully")

        return redirect("income")


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, "Income removed")
    return redirect("income")
