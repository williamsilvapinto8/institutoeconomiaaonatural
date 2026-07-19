from django.db import models


class ContentItem(models.Model):
    TYPE_CHOICES = [
        ('PDF', 'PDF'),
        ('VIDEO', 'Vídeo'),
        ('ARTICLE', 'Artigo'),
    ]
    title = models.CharField('Título', max_length=200)
    type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='PDF')
    description = models.TextField('Descrição', blank=True)
    file = models.FileField('Arquivo', upload_to='contents/', null=True, blank=True)
    external_link = models.URLField('Link Externo', blank=True)
    event = models.ForeignKey('events.Evento', on_delete=models.CASCADE, related_name='content_items', verbose_name='Evento')

    class Meta:
        verbose_name = 'Conteúdo'
        verbose_name_plural = 'Conteúdos'
        ordering = ['title']

    def __str__(self):
        return f'[{self.type}] {self.title}'
