from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category, CharityCase, Donation
from .forms import DonationForm

def home(request):
    categories = Category.objects.all()
    active_cases = CharityCase.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'charity/home.html', {
        'categories': categories,
        'active_cases': active_cases
    })

def case_list(request):
    category_id = request.GET.get('category')
    if category_id:
        cases = CharityCase.objects.filter(category_id=category_id, is_active=True)
    else:
        cases = CharityCase.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'charity/case_list.html', {
        'cases': cases,
        'categories': categories
    })

def case_detail(request, pk):
    case = get_object_or_404(CharityCase, pk=pk, is_active=True)
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.case = case
            donation.save()
            
            # Update case amount
            case.current_amount += donation.amount
            case.save()
            
            messages.success(request, 'Thank you for your donation! Your contribution will help make a difference.')
            return redirect('charity:case_detail', pk=pk)
    else:
        form = DonationForm()
    
    recent_donations = case.donations.order_by('-created_at')[:5]
    return render(request, 'charity/case_detail.html', {
        'case': case,
        'form': form,
        'recent_donations': recent_donations
    })
