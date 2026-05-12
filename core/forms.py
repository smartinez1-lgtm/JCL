"""Forms used by inventory management, authentication, and cashier operations."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Branch, Item, UserBranchAssignment


THEME_CHOICES = [
    ("pink", "JCL Pink"),
    ("blue", "Ocean Blue"),
    ("green", "Fresh Green"),
    ("dark", "Night Mode"),
]


class ItemForm(forms.ModelForm):
    """Form used to create and update inventory items."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Branch.objects.get_or_create(name="Main Branch", defaults={"is_active": True})
        self.fields["branch"].queryset = Branch.objects.filter(is_active=True).order_by("name")

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


class BranchForm(forms.ModelForm):
    """Form used by admins to create and update store branches."""

    class Meta:
        model = Branch
        fields = ["name", "address", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Branch name"}),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Optional branch address"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class AdminUserCreationForm(UserCreationForm):
    """Admin-only form for creating approved system users."""

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
    )
    is_staff = forms.BooleanField(
        required=False,
        label="Admin access",
        help_text="Allow this user to manage inventory, branches, and accounts.",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        help_text="Assign this user to a branch.",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "is_staff", "branch", "password1", "password2")
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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.is_active = True
        user.is_staff = self.cleaned_data.get("is_staff", False)
        if user.is_staff:
            user.is_superuser = False
        if commit:
            user.save()
            branch = self.cleaned_data.get("branch")
            if branch:
                UserBranchAssignment.objects.update_or_create(user=user, defaults={"branch": branch})
        return user


class UserBranchAssignmentForm(forms.Form):
    """Assign an existing non-admin user to a branch."""

    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        empty_label="No branch",
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )


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


class ThemeSettingsForm(forms.Form):
    """Stores the user's preferred website theme in their session."""

    theme = forms.ChoiceField(
        choices=THEME_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "theme-radio"}),
    )


class AdminSetupForm(forms.Form):
    """One-time production form for creating a staff superuser."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Admin username"}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Admin password"}),
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
