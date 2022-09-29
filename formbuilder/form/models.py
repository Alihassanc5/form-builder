from django import forms
from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField, FORM_FIELD_CHOICES, AbstractFormSubmission
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
        return forms.FileField(**options)

    def create_scale_field(self, field, options):
        return forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range',
                                                                  'min': '0',
                                                                  'max': '10',
                                                                  'id': 'myRange'}), required=False)


class FormUploadedFile(models.Model):
    file = models.FileField(upload_to="files/%Y/%m/%d")
    field_name = models.CharField(blank=True, max_length=254)


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

    def process_form_submission(self, form):

        file_form_fields = [field.clean_name for field in self.get_form_fields() if field.field_type == 'file']

        for (field_name, field_value) in form.cleaned_data.items():
            if field_name in file_form_fields:
                uploaded_file = FormUploadedFile.objects.create(
                    file=field_value,
                    field_name=field_name
                )

                # store a reference to the pk (as this can be converted to JSON)
                form.cleaned_data[field_name] = uploaded_file.file.url

        return self.get_submission_class().objects.create(
            form_data=form.cleaned_data,
            page=self,
        )


