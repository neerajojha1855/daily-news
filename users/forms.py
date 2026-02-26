from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

class UserPreferenceForm(forms.ModelForm):
    # A simple comma-separated or multiple select for categories could be used
    # But for simplicity, we mock it as a CharField that parses into JSON OR use a preset list
    categories = forms.MultipleChoiceField(
        choices=[
            ('technology', 'Technology'), 
            ('business', 'Business'), 
            ('sports', 'Sports'), 
            ('entertainment', 'Entertainment'),
            ('health', 'Health'),
            ('science', 'Science'),
            ('politics', 'Politics'),
            ('world', 'World News')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = [] # Custom fields handle preferences

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.preferences:
            self.fields['categories'].initial = self.instance.preferences.get('categories', [])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.preferences = {'categories': self.cleaned_data.get('categories', [])}
        if commit:
            user.save()
        return user
