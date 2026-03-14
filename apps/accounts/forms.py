from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your login ID',
            'class': 'form-input',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-input',
        })
    )


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'class': 'form-input',
        })
    )
    password2 = forms.CharField(
        label='Re-enter Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'form-input',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a login ID',
                'class': 'form-input',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'form-input',
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Must be 6-12 characters as per mockup rules
        if len(username) < 6 or len(username) > 12:
            raise forms.ValidationError(
                'Login ID must be between 6 and 12 characters.'
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                'This login ID is already taken.'
            )
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        # Must have uppercase, lowercase, special char, 8+ chars
        if len(password) < 8:
            raise forms.ValidationError(
                'Password must be at least 8 characters long.'
            )
        if not any(c.isupper() for c in password):
            raise forms.ValidationError(
                'Password must contain at least one uppercase letter.'
            )
        if not any(c.islower() for c in password):
            raise forms.ValidationError(
                'Password must contain at least one lowercase letter.'
            )
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise forms.ValidationError(
                'Password must contain at least one special character.'
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user