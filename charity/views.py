from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from decimal import Decimal
from .models import Category, CharityCase, Donation, UserProfile
from .forms import DonationForm, UserRegistrationForm, UserProfileForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()

def home(request):
    featured_cases = CharityCase.objects.filter(status='active').order_by('-created_at')[:3]
    categories = Category.objects.all()
    return render(request, 'charity/home.html', {
        'active_cases': featured_cases,
        'categories': categories
    })

def case_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    cases = CharityCase.objects.select_related('category')
    
    if category_id:
        cases = cases.filter(category_id=category_id)
    if search_query:
        cases = cases.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    active_cases = cases.filter(status='active')
    completed_cases = cases.filter(status='completed')
    
    active_paginator = Paginator(active_cases, 6)
    completed_paginator = Paginator(completed_cases, 6)
    
    active_page = request.GET.get('active_page', 1)
    completed_page = request.GET.get('completed_page', 1)
    
    active_cases = active_paginator.get_page(active_page)
    completed_cases = completed_paginator.get_page(completed_page)
    
    categories = Category.objects.all()
    
    return render(request, 'charity/case_list.html', {
        'active_cases': active_cases,
        'completed_cases': completed_cases,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query
    })

def case_detail(request, pk):
    case = get_object_or_404(CharityCase, pk=pk)
    recent_donations = case.donations.select_related('user').order_by('-created_at')[:5]
    
    if case.target_amount > 0:
        percentage = (case.current_amount / case.target_amount) * 100
    else:
        percentage = 0
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            remaining = case.target_amount - case.current_amount
            
            if amount > remaining:
                messages.error(request, _('Donation amount exceeds remaining target.'))
                return redirect('charity:case_detail', pk=pk)
            
            donation = form.save(commit=False)
            donation.case = case
            donation.user = request.user
            donation.save()
            
            case.current_amount += amount
            if case.current_amount >= case.target_amount:
                case.status = 'completed'
            case.save()
            
            messages.success(request, _('Thank you for your donation!'))
            return redirect('charity:case_detail', pk=pk)
    else:
        form = DonationForm()
    
    return render(request, 'charity/case_detail.html', {
        'case': case,
        'recent_donations': recent_donations,
        'form': form,
        'percentage': percentage
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

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    donations = request.user.donations.select_related('case').order_by('-created_at')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully!'))
            return redirect('charity:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'charity/profile.html', {
        'form': form,
        'donations': donations
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('Account created successfully! You can now log in.'))
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'charity/register.html', {'form': form})
