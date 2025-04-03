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
