# Charity Website Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technical Stack](#technical-stack)
3. [Project Structure](#project-structure)
4. [Database Models](#database-models)
5. [Views and Controllers](#views-and-controllers)
6. [Templates and Frontend](#templates-and-frontend)
7. [Internationalization](#internationalization)
8. [Static and Media Files](#static-and-media-files)
9. [Security Features](#security-features)
10. [Performance Optimizations](#performance-optimizations)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Future Improvements](#future-improvements)

## Project Overview

The Charity Website is a Django-based web application that facilitates charitable donations and case management. It allows users to:
- Browse and search for charity cases
- Make donations to specific cases
- Track donation progress
- View case categories
- Switch between English and Persian languages

### Key Features
- Multi-language support (English and Persian)
- Responsive design with Bootstrap
- Real-time donation tracking
- Image upload for cases
- Category-based organization
- Progress visualization
- Secure payment processing
- Admin interface for case management

## Technical Stack

### Backend
- **Framework**: Django 5.1.7
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Template Engine**: Django Templates
- **Authentication**: Django's built-in auth system
- **Internationalization**: Django's i18n system

### Frontend
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons
- **Fonts**: Google Fonts (Inter)
- **JavaScript**: Vanilla JS
- **Responsive Design**: Mobile-first approach

## Project Structure

```
CharityWebsitePython/
├── charity/                    # Main application
│   ├── migrations/            # Database migrations
│   │   ├── 0001_initial.py   # Initial migration
│   │   ├── 0002_add_category.py # Added Category model
│   │   └── 0003_add_donation.py # Added Donation model
│   ├── static/                # Static files
│   │   ├── css/              # Stylesheets
│   │   ├── js/               # JavaScript files
│   │   └── images/           # Static images
│   ├── templates/            # HTML templates
│   │   ├── base.html        # Base template
│   │   ├── home.html        # Homepage
│   │   ├── case_list.html   # Case listing
│   │   └── case_detail.html # Case details
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── urls.py              # URL routing
│   └── views.py             # View functions
├── charity_project/          # Project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── locale/                   # Translation files
│   ├── en/                  # English translations
│   └── fa/                  # Persian translations
└── manage.py                # Django management script
```

## Database Models

### CharityCase
```python
class CharityCase(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    image = models.ImageField(upload_to='charity_cases/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Donation
```python
class Donation(models.Model):
    case = models.ForeignKey(CharityCase, on_delete=models.CASCADE, related_name='donations')
    donor_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Category
```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Views and Controllers

### Home View
```python
def home(request):
    featured_cases = CharityCase.objects.filter(status='active')[:3]
    categories = Category.objects.all()
    return render(request, 'charity/home.html', {
        'featured_cases': featured_cases,
        'categories': categories
    })
```

### Case List View
```python
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
    
    # ... pagination logic
```

### Donation Processing
```python
def make_donation(request, pk):
    case = get_object_or_404(CharityCase, pk=pk)
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            remaining = case.target_amount - case.current_amount
            
            if amount > remaining:
                messages.error(request, _('Donation amount exceeds remaining target.'))
                return redirect('charity:case_detail', pk=pk)
            
            donation = form.save(commit=False)
            donation.case = case
            donation.save()
            
            case.current_amount += amount
            if case.current_amount >= case.target_amount:
                case.status = 'completed'
            case.save()
            
            messages.success(request, _('Thank you for your donation!'))
            return redirect('charity:case_detail', pk=pk)
```

## Templates and Frontend

### Base Template
```html
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}" dir="{% if LANGUAGE_CODE == 'fa' %}rtl{% else %}ltr{% endif %}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% trans "Charity Website" %}{% endblock %}</title>
    <!-- Bootstrap CSS -->
    <!-- Custom CSS -->
    {% if LANGUAGE_CODE == 'fa' %}
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css">
    {% endif %}
</head>
<body>
    <!-- Navigation -->
    <!-- Messages -->
    <!-- Main Content -->
    <!-- Footer -->
</body>
</html>
```

### Case Detail Template
```html
<div class="card">
    <div class="card-body">
        <h1 class="card-title h2 mb-4">{{ case.title }}</h1>
        
        <div class="progress mb-4">
            <div class="progress-bar" role="progressbar" 
                 style="width: {{ percentage|floatformat:1 }}%"
                 aria-valuenow="{{ percentage|floatformat:1 }}" 
                 aria-valuemin="0" 
                 aria-valuemax="100">
                {{ percentage|floatformat:1 }}%
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <h5 class="text-muted mb-1">{% trans "Raised" %}</h5>
                <h3 class="mb-0">${{ case.current_amount|floatformat:2 }}</h3>
            </div>
            <div class="col-md-6">
                <h5 class="text-muted mb-1">{% trans "Goal" %}</h5>
                <h3 class="mb-0">${{ case.target_amount|floatformat:2 }}</h3>
            </div>
        </div>
        
        <p class="card-text">{{ case.description|linebreaks }}</p>
        
        <span class="badge bg-primary">{{ case.category.name }}</span>
    </div>
</div>
```

## Internationalization

### Translation Files
```
locale/
├── en/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── fa/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo
```

### Translation Process
1. Mark strings in templates:
```html
{% trans "Charity Website" %}
{% blocktrans %}Your contribution can help change lives{% endblocktrans %}
```

2. Extract translations:
```bash
python manage.py makemessages -l en
python manage.py makemessages -l fa
```

3. Compile translations:
```bash
python manage.py compilemessages
```

## Static and Media Files

### Configuration
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### File Structure
```
static/
└── charity/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── images/
        └── default-case.jpg

media/
└── charity_cases/
    └── [uploaded_images]
```

## Security Features

### CSRF Protection
```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### Form Validation
```python
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donor_name', 'amount', 'message']
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError(_('Amount must be greater than zero.'))
        return amount
```

## Performance Optimizations

### Database Optimization
```python
# Using select_related
cases = CharityCase.objects.select_related('category')

# Using values_list
donation_amounts = Donation.objects.filter(case=case).values_list('amount', flat=True)
```

### Template Caching
```html
{% cache 3600 case_detail case.pk %}
    <!-- case detail content -->
{% endcache %}
```

## Testing

### View Tests
```python
class CaseViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.case = CharityCase.objects.create(
            title='Test Case',
            description='Test Description',
            target_amount=1000,
            category=self.category
        )
    
    def test_case_detail_view(self):
        response = self.client.get(f'/cases/{self.case.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Case')
```

## Deployment

### Requirements
- Python 3.8+
- Django 5.1.7
- PostgreSQL (for production)
- Gunicorn (for production)
- Nginx (for production)

### Deployment Steps
1. Set up production environment
2. Configure production settings
3. Set up database
4. Collect static files
5. Configure web server
6. Set up SSL certificate
7. Configure domain

## Future Improvements

1. **Payment Integration**
   - Add payment gateway integration
   - Support multiple payment methods
   - Implement recurring donations

2. **User Accounts**
   - Add user registration and login
   - Donation history for users
   - Saved cases/favorites

3. **Enhanced Features**
   - Case updates and news
   - Donor testimonials
   - Social sharing
   - Email notifications

4. **Analytics**
   - Donation analytics
   - User behavior tracking
   - Case performance metrics

5. **Mobile App**
   - Native mobile application
   - Push notifications
   - Offline support

6. **API Development**
   - RESTful API
   - Third-party integration
   - Mobile app backend

7. **Content Management**
   - Rich text editor
   - Media library
   - Content scheduling

8. **Security Enhancements**
   - Two-factor authentication
   - Advanced rate limiting
   - Security headers

9. **Performance Optimization**
   - Caching strategy
   - Database optimization
   - Asset optimization

10. **Accessibility**
    - WCAG compliance
    - Screen reader support
    - Keyboard navigation 