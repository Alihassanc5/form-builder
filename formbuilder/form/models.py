from django import forms
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField, FORM_FIELD_CHOICES
from wagtail.contrib.forms.panels import FormSubmissionsPanel


class FormField(AbstractFormField):
    CHOICES = FORM_FIELD_CHOICES + (('file', 'File'), ('scale', 'Linear Scale'))

    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')
    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=CHOICES
    )

class CustomFormBuilder(FormBuilder):
    def create_file_field(self, field, options):
        return forms.FileField()

    def create_scale_field(self, field, options):
        return forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range',
                                                                  'min': '0',
                                                                  'max': '10',
                                                                  'id': 'myRange'}), required=False)

class FormPage(AbstractForm):
    form_builder = CustomFormBuilder
    description = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('description'),
        FieldPanel('thank_you_text'),
        InlinePanel('form_fields', label="Form fields"),
    ]
