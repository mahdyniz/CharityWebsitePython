from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from decimal import Decimal
from .models import Category, CharityCase, Donation
from .forms import DonationForm
from django.db.models import Q

def home(request):
    categories = Category.objects.all()
    active_cases = CharityCase.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'charity/home.html', {
        'categories': categories,
        'active_cases': active_cases
    })

def case_list(request):
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    completed_page = request.GET.get('completed_page', 1)
    
    # Base queryset for active cases
    active_cases = CharityCase.objects.filter(is_active=True).order_by('-created_at')
    
    # Base queryset for completed cases
    completed_cases = CharityCase.objects.filter(is_active=False).order_by('-created_at')
    
    # Apply search if provided
    if search_query:
        active_cases = active_cases.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        completed_cases = completed_cases.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Paginate active cases
    active_paginator = Paginator(active_cases, 6)
    try:
        active_cases = active_paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        active_cases = active_paginator.page(1)
    
    # Paginate completed cases
    completed_paginator = Paginator(completed_cases, 6)
    try:
        completed_cases = completed_paginator.page(completed_page)
    except (PageNotAnInteger, EmptyPage):
        completed_cases = completed_paginator.page(1)
    
    return render(request, 'charity/case_list.html', {
        'active_cases': active_cases,
        'completed_cases': completed_cases,
        'search_query': search_query
    })

def case_detail(request, pk):
    case = get_object_or_404(CharityCase, pk=pk)
    recent_donations = Donation.objects.filter(case=case).order_by('-created_at')[:5]
    
    # Calculate percentage
    if case.target_amount > 0:
        percentage = (case.current_amount / case.target_amount) * 100
    else:
        percentage = 0
    
    # Calculate remaining amount needed
    remaining_amount = case.target_amount - case.current_amount
    
    return render(request, 'charity/case_detail.html', {
        'case': case,
        'recent_donations': recent_donations,
        'percentage': percentage,
        'remaining_amount': remaining_amount
    })

def make_donation(request, pk):
    if request.method == 'POST':
        case = get_object_or_404(CharityCase, pk=pk)
        
        # Check if case is still active
        if not case.is_active:
            messages.error(request, "This case is no longer accepting donations.")
            return redirect('charity:case_detail', pk=pk)
        
        donor_name = request.POST.get('donor_name')
        amount = request.POST.get('amount')
        message = request.POST.get('message')
        
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            
            # Calculate remaining amount needed
            remaining_amount = case.target_amount - case.current_amount
            
            # Check if donation amount exceeds remaining amount needed
            if amount > remaining_amount:
                messages.error(request, f"Please donate ${remaining_amount:.2f} or less to complete this case.")
                return redirect('charity:case_detail', pk=pk)
                
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
        
        # Check if case is now complete
        if case.current_amount >= case.target_amount:
            case.is_active = False
            messages.success(request, f"Thank you for your donation! This case has been fully funded!")
        else:
            messages.success(request, f"Thank you for your donation of ${amount:.2f}!")
        
        case.save()
        return redirect('charity:case_detail', pk=pk)
    
    return redirect('charity:case_detail', pk=pk)
