from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'category', 'description', 'location']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan judul laporan'
            }),

            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Infrastruktur, Lingkungan, dll'
            }),

            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lokasi kejadian'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Jelaskan detail laporan secara lengkap...'
            }),
        }

        labels = {
            'title': 'Judul',
            'category': 'Kategori',
            'description': 'Deskripsi',
            'location': 'Lokasi',
        }