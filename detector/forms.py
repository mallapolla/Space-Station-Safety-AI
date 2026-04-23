from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Upload space station safety image",
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
    )


class VideoUploadForm(forms.Form):
    video = forms.FileField(
        label="Upload inspection video",
        widget=forms.ClearableFileInput(attrs={"accept": "video/*"}),
    )
