from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean_email(self):
        """Ensure Unique Email."""
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'A user with that email already exists.')
        return email


class AddFriendForm(forms.Form):
    email = forms.CharField(max_length=100, required=True)

    def find_user(self):
        """Ensure Unique Email."""
        email = self.cleaned_data.get('email')
        user = User.objects.get(email=email)
        if User.objects.filter(email=email).count() == 0:
            raise forms.ValidationError(u'No user with that email.')
        else:
            return email