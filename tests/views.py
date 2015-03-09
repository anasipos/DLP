import datetime

from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from models import Test, UserTest, PageInTest, UserPage, UserQuestion, QuestionOnPage, QuestionAnswer, UserAnswer
from forms import nested_formset_factory, UserQuestionForm, UserAnswerForm, UserAnswersFormset


class ChooseTestView(ListView):
    # generic tests -> not user specific yet
    model = Test


class TestResults(DetailView):
    template_name = 'tests/results.html'
    model = UserTest

    def get_context_data(self, **kwargs):
        context = super(TestResults, self).get_context_data(**kwargs)
        questions = []
        for page in self.object.userpage_set.all():
            for question in page.userquestion_set.all():
                qa = {'text': question.text}
                answers = []
                for answer in question.useranswer_set.all():
                    a = {
                        'text': answer.text,
                        'is_selected': answer.is_selected,
                        'is_correct': answer.question_answer.score > 0
                    }
                    answers.append(a)
                qa['answers'] = answers
                questions.append(qa)

        context['questions'] = questions
        return context


def create_answers_for_user_question(user_question, question):
    for answer in question.answer.all():
        qa = QuestionAnswer.objects.get(question=question, answer=answer)
        user_answer = UserAnswer(text=answer.text, user_question=user_question, question_answer=qa, is_selected=False)
        user_answer.save()


def create_questions_for_user_page(user_page, page):
    for question in page.questions.all():
        question_index = QuestionOnPage.objects.get(question=question, page=page).question_index
        user_question = UserQuestion(text=question.text, is_answered=False, user_page=user_page,
                                     question_index=question_index)
        user_question.save()
        create_answers_for_user_question(user_question, question)


def create_pages_for_user_test(user_test, test):
    for page in test.pages.all():
        page_index = PageInTest.objects.get(test=test, page=page).page_index
        user_page = UserPage(page_index=page_index, user_test=user_test)
        user_page.save()
        create_questions_for_user_page(user_page, page)


class CreateUserTest(CreateView):
    model = UserTest
    template_name = 'tests/create-user-test.html'
    fields = ['user']

    def __init__(self):
        super(CreateUserTest, self).__init__()
        # test_id = self.kwargs['test_id']
        # self.test = Test.objects.get(pk=test_id)

    def get_context_data(self, **kwargs):
        context = super(CreateUserTest, self).get_context_data(**kwargs)
        test_id = self.kwargs['test_id']
        self.test = Test.objects.get(pk=test_id)
        context['test'] = self.test
        return context

    def form_valid(self, form):
        test_id = self.kwargs['test_id']
        self.test = Test.objects.get(pk=test_id)

        form.instance.test = self.test
        form.instance.date_taken = datetime.date.today()
        form.instance.save()
        create_pages_for_user_test(form.instance, self.test)
        self.first_page_id = UserPage.objects.get(user_test=form.instance, page_index=1).id
        return super(CreateUserTest, self).form_valid(form)

    def get_success_url(self):
        return reverse('tests:user-page', kwargs={'pk': self.first_page_id})


class TakeTestView(UpdateView):
    model = UserPage

    def get_object(self, queryset=None):
        object = super(TakeTestView, self).get_object(queryset)
        self.usertest = object.user_test

        if object.page_index == 1:
            self.has_prev = False
        else:
            self.has_prev = True

        next_page_id = -1
        if object.page_index < object.user_test.userpage_set.count():
            next_page_id = object.user_test.userpage_set.get(page_index=object.page_index + 1).id
        self.next_page_id = next_page_id

        prev_page_id = -1
        if object.page_index > 1:
            prev_page_id = object.user_test.userpage_set.get(page_index=object.page_index - 1).id
        self.prev_page_id = prev_page_id


        self.is_last_page = True if self.next_page_id is -1 else False

        return object

    def get_context_data(self, **kwargs):
        context = super(TakeTestView, self).get_context_data(**kwargs)

        context['next_page_id'] = self.next_page_id
        context['last_page'] = self.is_last_page
        context['has_prev'] = self.has_prev

        return context

    def get_template_names(self):
        return ['tests/test-page.html']

    def get_form_class(self):
        return nested_formset_factory(
            UserPage,
            UserQuestion,
            # fields=['text'],
            exclude=['text', 'question_index'],
            max_num=1,
            error_messages='Please answer the question',
            form=UserQuestionForm,
            nested_formset=inlineformset_factory(
                UserQuestion,
                UserAnswer,
                max_num=1,
                form=UserAnswerForm,
                formset=UserAnswersFormset,
                # exclude=['text', 'question_answer'],
                # fields=['text', 'is_selected']
            )
            # UserAnswer,
        )


    def get_success_url(self):
        prev = False
        if self.request.POST['action'] == 'Prev':
            prev = True

        if prev:
            return reverse('tests:user-page', kwargs={'pk': self.prev_page_id})

        if not self.is_last_page:
            return reverse('tests:user-page', kwargs={'pk': self.next_page_id})

        return reverse('tests:results', kwargs={'pk': self.usertest.id})

