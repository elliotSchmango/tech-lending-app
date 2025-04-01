from django import forms

from .models import Profile, Item, Collection

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']

class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['title', 'identifier', 'status', 'location', 'description', 'image']

    def save(self, commit=True):
        item = super().save(commit=False)
        if commit:
            item.save()
        return item

class CollectionFormLibrarian(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'visibility', 'items']
        widgets = {
            'items': forms.CheckboxSelectMultiple, 
        }

class CollectionFormPatron(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'items']
        widgets = {
            'items': forms.CheckboxSelectMultiple, 
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force visibility to "public" for all patron-created collections
        self.instance.visibility = 'public'
