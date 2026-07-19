from django.db import models
from accounts.models import Benegnado


class ImpactDimension(models.Model):
    code = models.CharField('Código', max_length=10, unique=True)
    name = models.CharField('Nome', max_length=200)
    weight = models.DecimalField('Peso', max_digits=4, decimal_places=2, default=0.25)

    class Meta:
        verbose_name = 'Dimensão de Impacto'
        verbose_name_plural = 'Dimensões de Impacto'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'


class ImpactQuestion(models.Model):
    dimension = models.ForeignKey(
        ImpactDimension, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='questions', verbose_name='Dimensão'
    )
    text = models.TextField('Texto da Pergunta')
    order = models.PositiveIntegerField('Ordem', default=0)
    is_open = models.BooleanField('É aberta (discursiva)?', default=False)

    class Meta:
        verbose_name = 'Pergunta de Impacto'
        verbose_name_plural = 'Perguntas de Impacto'
        ordering = ['order']

    def __str__(self):
        return f'[{self.order}] {self.text[:80]}'


class ImpactForm(models.Model):
    event = models.ForeignKey('events.Evento', on_delete=models.CASCADE, related_name='impact_forms', verbose_name='Evento')
    name = models.CharField('Nome do Formulário', max_length=200)

    class Meta:
        verbose_name = 'Formulário de Impacto'
        verbose_name_plural = 'Formulários de Impacto'

    def __str__(self):
        return f'{self.name} — {self.event}'


class ImpactResponse(models.Model):
    impact_form = models.ForeignKey(ImpactForm, on_delete=models.CASCADE, related_name='responses', verbose_name='Formulário')
    benegnado = models.ForeignKey(Benegnado, on_delete=models.CASCADE, related_name='impact_responses', verbose_name='Benegnado')
    created_at = models.DateTimeField('Respondido em', auto_now_add=True)

    class Meta:
        verbose_name = 'Resposta de Impacto'
        verbose_name_plural = 'Respostas de Impacto'
        unique_together = ('impact_form', 'benegnado')

    def __str__(self):
        return f'{self.benegnado} — {self.impact_form}'

    def calculate_iih(self):
        """Calcula o Índice de Impacto Humano (IIH) para esta resposta."""
        from decimal import Decimal
        dimension_scores = {}
        answers = self.answers.filter(impact_question__is_open=False).select_related('impact_question__dimension')
        for answer in answers:
            dim = answer.impact_question.dimension
            if dim:
                if dim.code not in dimension_scores:
                    dimension_scores[dim.code] = {'sum': 0, 'count': 0, 'weight': dim.weight}
                if answer.value:
                    dimension_scores[dim.code]['sum'] += answer.value
                    dimension_scores[dim.code]['count'] += 1
        iih = Decimal('0')
        for dim_code, data in dimension_scores.items():
            if data['count'] > 0:
                score = Decimal(str(data['sum'])) / Decimal(str(data['count']))
                iih += score * data['weight']
        return round(float(iih) * 20, 2)


class ImpactAnswer(models.Model):
    impact_response = models.ForeignKey(ImpactResponse, on_delete=models.CASCADE, related_name='answers', verbose_name='Resposta')
    impact_question = models.ForeignKey(ImpactQuestion, on_delete=models.CASCADE, verbose_name='Pergunta')
    value = models.PositiveSmallIntegerField('Valor Likert (1-5)', null=True, blank=True)
    text_answer = models.TextField('Resposta Discursiva', blank=True)

    class Meta:
        verbose_name = 'Resposta Individual'
        verbose_name_plural = 'Respostas Individuais'

    def __str__(self):
        return f'R{self.impact_response_id} — Q{self.impact_question_id}'
