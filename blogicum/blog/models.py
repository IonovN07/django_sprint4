from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BasePublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')

    class Meta:
        abstract = True


class Category(BasePublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.')

    class Meta():
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('-title',)

    def __str__(self):
        return f'{self.title[:21]} {self.description[:21]}'


class Location(BasePublishedModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta():
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('-name',)

    def __str__(self):
        return self.name[:21]



class Post(BasePublishedModel):
    related_name = 'posts'

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=related_name,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name=related_name,
        verbose_name='Местоположение')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name=related_name,
        verbose_name='Категория')
    image = models.ImageField(
        upload_to='post_images',
        blank=True,
        verbose_name='Фото')

    class Meta():
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'category', 'pub_date'),
                name='Unique post constraint',
            ),
        )

    def __str__(self):
        return (f'{self.title[:21]} {self.text[:21]} '
                f'{self.category.title[:21]}')


class Comment(models.Model):
    text = models.TextField(max_length=256, verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments',
        verbose_name='Автор комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments',
        verbose_name='Комментарий поста')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:21]