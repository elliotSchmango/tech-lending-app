from django import forms
from .models import Profile, Item, Collection

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']

class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['title', 'identifier', 'status', 'location', 'description', 'collections', 'image']
        widgets = {
            'collections': forms.CheckboxSelectMultiple()
        }

    def save(self, commit=True):
        item = super().save(commit=False)
        if commit:
            item.save()
        return item

class CollectionFormLibrarian(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'visibility']

class CollectionFormPatron(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description']
