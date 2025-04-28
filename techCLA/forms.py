from django import forms

from .models import Profile, Item, Collection, Review, RequestAccess

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['title', 'identifier', 'status', 'location', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 100px;'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

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
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 100px;'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'items': forms.CheckboxSelectMultiple(),
        }


class CollectionFormPatron(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'items']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 100px;'}),
            'items': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force visibility to "public" for all patron-created collections
        self.instance.visibility = 'public'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 11)], attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RequestAccessForm(forms.ModelForm):
    class Meta:
        model = RequestAccess
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional message...'}),
        }