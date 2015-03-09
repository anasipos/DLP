from django.db import models


class Answer(models.Model):
    text = models.CharField(max_length=200)

    def __unicode__(self):
        return self.text


class Question(models.Model):
    text = models.CharField(max_length=200)
    answer = models.ManyToManyField(Answer, through='QuestionAnswer')

    def __unicode__(self):
        return self.text


class QuestionAnswer(models.Model):
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
    score = models.SmallIntegerField()


class PageDescription(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        abstract = True


class Page(PageDescription):
    questions = models.ManyToManyField(Question, through='QuestionOnPage')

    def __unicode__(self):
        return self.description


class QuestionOnPage(models.Model):
    question = models.ForeignKey(Question)
    page = models.ForeignKey(Page)
    question_index = models.PositiveSmallIntegerField()


class TestDescription(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Test(TestDescription):
    pages = models.ManyToManyField(Page, through='PageInTest')

    def __unicode__(self):
        return self.name


class PageInTest(models.Model):
    page = models.ForeignKey(Page)
    test = models.ForeignKey(Test)
    page_index = models.PositiveSmallIntegerField()


# user-specific model - needs to be cleaned from time to time....


class UserTest(TestDescription):
    user = models.CharField(max_length=50)
    date_taken = models.DateField()
    test = models.ForeignKey(Test)

    def __unicode__(self):
        return self.name


class UserPage(PageDescription):
    page_index = models.PositiveSmallIntegerField()
    user_test = models.ForeignKey(UserTest)

    def __unicode__(self):
        return self.description


class UserQuestion(models.Model):
    text = models.CharField(max_length=100)
    is_answered = models.BooleanField()
    user_page = models.ForeignKey(UserPage)
    question_index = models.PositiveSmallIntegerField()

    # def get_text(self):
    # return UserAnswer.objects.filter(user_question=self)[0].question_answer.question.text

    def __unicode__(self):
        return self.text


class UserAnswer(models.Model):
    user_question = models.ForeignKey(UserQuestion)
    question_answer = models.ForeignKey(QuestionAnswer)
    text = models.CharField(max_length=100)
    is_selected = models.BooleanField()

    # def get_text(self):
    # return self.question_answer.answer.text

    def __unicode__(self):
        return self.text


# class Recipe(models.Model):
# title = models.CharField(max_length=255)
#     description = models.TextField()
#
#
# class Ingredient(models.Model):
#     recipe = models.ForeignKey(Recipe)
#     description = models.CharField(max_length=255)
#
#
# class Instruction(models.Model):
#     recipe = models.ForeignKey(Recipe)
#     number = models.PositiveSmallIntegerField()
#     description = models.TextField()




class Block(models.Model):
    description = models.CharField(max_length=255)


class Building(models.Model):
    block = models.ForeignKey(Block)
    address = models.CharField(max_length=255)


class Tenant(models.Model):
    building = models.ForeignKey(Building)
    name = models.CharField(max_length=255)
    unit = models.CharField(
        blank=False,
        max_length=255,
    )