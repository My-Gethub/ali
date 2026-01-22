from django import forms
from .models import Car
from django.contrib.auth.models import User
from .models import Car, Accessory, CarInquiry, CarReview
from django.contrib.auth.forms import UserCreationForm

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'category', 'title', 'price', 'old_price', 'image', 'description',
            'model_year', 'mileage', 'fuel_type', 'transmission', 'engine', 'status',
            'air_conditioner', 'power_windows', 'power_steering', 'central_locking',
            'abs', 'airbags', 'leather_seats'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'transmission': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CarForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = [
            'category', 'title', 'price', 'old_price', 'image', 'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AccessoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super(AdminUserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class AdminUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    is_staff = forms.BooleanField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'is_staff', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super(AdminUserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class CarInquiryForm(forms.ModelForm):
    class Meta:
        model = CarInquiry
        fields = ['name', 'email', 'phone', 'message']
    
    def __init__(self, *args, **kwargs):
        super(CarInquiryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            if field == 'message':
                self.fields[field].widget.attrs.update({'rows': 4})

class CarReviewForm(forms.ModelForm):
    class Meta:
        model = CarReview
        fields = ['rating', 'comment']
    
    def __init__(self, *args, **kwargs):
        super(CarReviewForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            if field == 'comment':
                self.fields[field].widget.attrs.update({'rows': 4})

from .models import Category, BlogPost

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'image']
        
    def __init__(self, *args, **kwargs):
        super(BlogPostForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            if field == 'content':
                self.fields[field].widget.attrs.update({'rows': 10})
