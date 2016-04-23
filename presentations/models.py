# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import CharField, TextField
from django.utils.text import slugify
from unidecode import unidecode
from presentations.managers import SorterManager
from user_interface.models import ProjectUser


class ChangeAbstractModel(models.Model):
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True, null=True)
    modified_at = models.DateTimeField(verbose_name='Изменено', auto_now=True, null=True)

    class Meta:
        abstract = True


class Organisation(ChangeAbstractModel):
    name = models.CharField(verbose_name='Название организации', max_length=64)
    slug = models.SlugField(verbose_name='Слаг', null=True, blank=True)

    class Meta:
        db_table = 'organisations'
        verbose_name = 'Организация'
        verbose_name_plural = 'организации'

    def __str__(self):
        return self.name


class Presentation(ChangeAbstractModel):
    organisation = models.ForeignKey(Organisation, verbose_name='Организация')
    name = models.CharField(verbose_name='Название презентации', max_length=64)
    slug = models.SlugField(verbose_name='Слаг', null=True, blank=True)
    position = models.IntegerField(verbose_name='Позиция', default=0, editable=False)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    objects = SorterManager()

    class Meta:
        db_table = 'presentations'
        verbose_name = 'Презентация'
        verbose_name_plural = 'презентации'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        if self.position == 0:
            self.position = Presentation.objects.filter(organisation=self.organisation).count() + 1
        return super().save(*args, **kwargs)


def get_upload_path(instance, filename):
    return "{organisation}/{presentation}/{slide_id}/{file}".format(
        organisation=instance.presentation.organisation.slug,
        presentation=instance.presentation.slug,
        slide_id=instance.presentation.id,
        file=filename)


class CoreSlide(ChangeAbstractModel):
    presentation = models.ForeignKey(Presentation, verbose_name='Презентация')
    question = models.ForeignKey('Question', null=True, blank=True, verbose_name='Вопрос')
    image = models.ImageField(verbose_name='Изображение', blank=True, null=True, upload_to=get_upload_path)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(verbose_name='Слаг', null=True, blank=True)
    position = models.IntegerField(verbose_name='Позиция', default=0, editable=False)

    objects = SorterManager()


    class Meta:
        db_table = 'slides'
        verbose_name = 'Слайд'
        verbose_name_plural = 'слайды'

    @property
    def previous_slide(self):
        prev_slides = CoreSlide.objects.filter(presentation=self.presentation_id).\
            filter(position__lt=self.position)
        if prev_slides:
            return prev_slides.last()
        else:
            return False

    @property
    def next_slide(self):
        next_slides = CoreSlide.objects.filter(presentation=self.presentation_id).\
            filter(position__gt=self.position)
        if next_slides:
            return next_slides.first()
        else:
            return False

    def save(self, *args, **kwargs):
        if self.position == 0:
            self.position = CoreSlide.objects.filter(presentation=self.presentation).count() + 1
        super().save(*args, **kwargs)

        import PIL
        from PIL import Image

        basewidth = 700
        img = Image.open(self.image.path)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        img.save(self.image.path)

    def delete(self, using=None, keep_parents=False):
        super().delete()
        i = 1
        slide_list = CoreSlide.objects.filter(presentation=self.presentation)
        for slide in slide_list:
            slide.position = i
            slide.save()
            i += 1

    def __str__(self):
        return '{presentation} - {position}'.format(presentation=self.presentation, position=self.position)


class Question(models.Model):
    ANSWER_TYPE = (
        ('multi', 'Множественный выбор'),
        ('single', 'Единичный выбор'),
    )

    text = TextField(verbose_name='Текст вопроса')
    answers_type = CharField(verbose_name='Тип ответов', max_length=8, choices=ANSWER_TYPE, default='multi')
    organisation = models.ForeignKey(Organisation, null=True, blank=True)

    class Meta:
        db_table = 'questions'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question)
    position = models.IntegerField(default=0, editable=False)
    text = CharField(verbose_name='Текст ответа', max_length=64)
    is_right = models.BooleanField(verbose_name='Является правильным ответом', default=False)
    has_comment = models.BooleanField(verbose_name="Ответ с комментарием", default=False)

    objects = SorterManager()

    def __str__(self):
        return  self.text

    class Meta:
        db_table = 'answers'
        verbose_name = 'Ответ'
        verbose_name_plural = 'ответы'

    @property
    def previous_answer(self):
        prev_answers = Answer.objects.filter(question=self.question_id).filter(position__lt=self.position)
        if prev_answers:
            return prev_answers.last()
        else:
            return False

    @property
    def next_answer(self):
        next_answers = Answer.objects.filter(question=self.question_id).\
            filter(position__gt=self.position)
        if next_answers:
            return next_answers.first()
        else:
            return False

    def save(self, *args, **kwargs):
        if self.position == 0:
            self.position = Answer.objects.filter(question=self.question_id).count() + 1
        return super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        super().delete()
        i = 1
        answer_list = Answer.objects.filter(question=self.question_id)
        for answer in answer_list:
            answer.position = i
            answer.save()
            i += 1


class UserAnswer(models.Model):
    """
        наличие этой записи соответствует ответу user на вариант answer
        иногда может быть комментарий к ответу
    """
    user = models.ForeignKey(ProjectUser, verbose_name="Пользователь")
    answer = models.ForeignKey(Answer, verbose_name="Ответ")
    comment = TextField(verbose_name='Комментарий', blank=True, null=True)

    class Meta:
        db_table = 'user_answers'
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'ответы пользователей'
