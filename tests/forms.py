import django
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from models import UserPage, UserQuestion, UserAnswer


__author__ = 'anamaria.sipos'


class UserPageForm(ModelForm):
    class Meta:
        model = UserPage


class UserQuestionForm(ModelForm):
    class Meta:
        model = UserQuestion

    def clean(self):
        cleaned_data = super(UserQuestionForm, self).clean()
        print 'Question Form: ', cleaned_data
        return cleaned_data

    def is_valid(self):
        v = super(UserQuestionForm, self).is_valid()
        if not v:
            self.cleaned_data['text'] = self.instance.text
            self.cleaned_data['question_index'] = self.instance.question_index
            self._errors = {}
            v = True

        print 'Question is_valid: ', v
        return v


class UserAnswerForm(ModelForm):
    class Meta:
        model = UserAnswer

    def clean(self):
        cleaned_data = super(UserAnswerForm, self).clean()
        cleaned_data['text'] = self.instance.text
        cleaned_data['question_answer'] = self.instance.question_answer
        self._errors = {}
        print 'Answer form clean(): ', cleaned_data
        return cleaned_data

    def is_valid(self):
        v = super(UserAnswerForm, self).is_valid()
        print 'Answer form is_valid: ', v
        return v


class UserAnswersFormset(BaseInlineFormSet):
    def clean(self):

        cleaned_data = super(UserAnswersFormset, self).clean()
        print 'Answer FormSet clean(): ', cleaned_data

        is_answered = False
        for answer_form in self.forms:
            selected = answer_form.cleaned_data['is_selected']
            if selected:
                is_answered = True

        if not is_answered:
            self.error_message = 'Question is not answered'
            raise ValidationError('Question is not answered')


class BaseNestedFormset(BaseInlineFormSet):
    def add_fields(self, form, index):

        # allow the super class to create the fields as usual
        super(BaseNestedFormset, self).add_fields(form, index)

        form.nested = self.nested_formset_class(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='%s-%s' % (
                form.prefix,
                self.nested_formset_class.get_default_prefix(),
            ),
        )

    def is_valid(self):
        result = super(BaseNestedFormset, self).is_valid()

        if self.is_bound:
            # look at any nested formsets, as well
            for form in self.forms:
                if not self._should_delete_form(form):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):

        result = super(BaseNestedFormset, self).save(commit=commit)

        for form in self.forms:
            if not self._should_delete_form(form):
                form.nested.save(commit=commit)

        return result

    @property
    def media(self):
        return self.empty_form.media + self.empty_form.nested.media


class BaseNestedModelForm(ModelForm):
    def has_changed(self):
        return (
            super(BaseNestedModelForm, self).has_changed() or
            self.nested.has_changed()
        )


def nested_formset_factory(parent_model, model, nested_formset,
                           form=BaseNestedModelForm,
                           formset=BaseNestedFormset, fk_name=None,
                           fields=None, exclude=None, extra=0,
                           can_order=False, can_delete=True,
                           max_num=None, formfield_callback=None,
                           widgets=None, validate_max=False,
                           localized_fields=None, labels=None,
                           help_texts=None, error_messages=None):
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': formset,
        'extra': extra,
        'can_delete': can_delete,
        'can_order': can_order,
        'fields': fields,
        'exclude': exclude,
        'max_num': max_num,
    }

    if django.VERSION >= (1, 6):
        kwargs.update({
            'widgets': widgets,
            'validate_max': validate_max,
            'localized_fields': localized_fields,
            'labels': labels,
            'help_texts': help_texts,
            'error_messages': error_messages,
        })

        if kwargs['fields'] is None:
            kwargs['fields'] = [
                field.name
                for field in model._meta.local_fields
            ]

    NestedFormSet = inlineformset_factory(
        parent_model,
        model,
        **kwargs
    )
    NestedFormSet.nested_formset_class = nested_formset

    return NestedFormSet
