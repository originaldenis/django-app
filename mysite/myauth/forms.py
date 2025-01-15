from django.db.models import ImageField
from django.forms import ModelForm

from .models import Profile


class AboutMeForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]
