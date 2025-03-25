from .models import User, IFTAR
from django import forms
from django.forms import ModelForm, DateInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    first_name = forms.CharField(max_length=200, required=True)
    last_name = forms.CharField(max_length=200, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'password1',
            'password2',
        ]

class OrganizeForm(ModelForm):
    title = forms.CharField(max_length=100)
    location = forms.CharField()
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'custom-select',
        })
    )
    time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['T%H:%M']
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participants'].label_from_instance = lambda obj: obj.username

    class Meta:
        model = IFTAR
        fields = [
            'title', 
            'location', 
            'participants',
            'time'
        ]