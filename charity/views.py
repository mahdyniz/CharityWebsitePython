from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from decimal import Decimal
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
    search_query = request.GET.get('search')
    
    cases = CharityCase.objects.filter(is_active=True)
    
    if category_id:
        cases = cases.filter(category_id=category_id)
    
    if search_query:
        cases = cases.filter(title__icontains=search_query) | cases.filter(description__icontains=search_query)
    
    paginator = Paginator(cases, 9)  # Show 9 cases per page
    page_number = request.GET.get('page')
    cases = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    return render(request, 'charity/case_list.html', {
        'cases': cases,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
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

def make_donation(request, pk):
    if request.method == 'POST':
        case = get_object_or_404(CharityCase, pk=pk)
        donor_name = request.POST.get('donor_name')
        amount = request.POST.get('amount')
        message = request.POST.get('message')
        
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid amount.")
            return redirect('charity:case_detail', pk=pk)
        
        donation = Donation.objects.create(
            case=case,
            donor_name=donor_name,
            amount=amount,
            message=message
        )
        
        case.current_amount += amount
        case.save()
        
        messages.success(request, f"Thank you for your donation of ${amount:.2f}!")
        return redirect('charity:case_detail', pk=pk)
    
    return redirect('charity:case_detail', pk=pk)
