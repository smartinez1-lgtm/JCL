"""Forms used by inventory management, authentication, and cashier operations."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Item


class ItemForm(forms.ModelForm):
    """Form used to create and update inventory items."""

    class Meta:
        model = Item
        fields = ["branch", "name", "description", "price", "quantity"]
        widgets = {
            "branch": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Item name"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Optional description"}
            ),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
        }


class CartAddForm(forms.Form):
    """Adds an item to the session cart from the cashier page."""

    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )


class CartUpdateForm(forms.Form):
    """Updates cart quantities inline on the cashier page."""

    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )


class SearchForm(forms.Form):
    """Simple search bar for filtering items by name."""

    q = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search items by name...",
            }
        ),
    )


class SignUpForm(UserCreationForm):
    """Simple user registration form for first-time cashier/admin accounts."""

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Choose a username"})
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Create a password"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Confirm password"})

    def clean_username(self):
        username = self.cleaned_data["username"]
        user_model = get_user_model()

        if user_model.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken. Please choose another one.")

        return username
