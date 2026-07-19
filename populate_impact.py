import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from impact_forms.models import ImpactDimension, ImpactQuestion

def run():
    print("Clearing existing questions and dimensions...")
    ImpactQuestion.objects.all().delete()
    ImpactDimension.objects.all().delete()

    dimensions_data = [
        {"code": "D1", "name": "Consciência e Identidade", "weight": 0.25, "questions": [
            "Sinto que minhas decisões estão mais alinhadas com meu propósito.",
            "Compreendo melhor meus padrões emocionais.",
            "Evito culpar fatores externos quando não alcanço os resultados esperados.",
            "A Escola de Oportunidade marcou uma virada importante na minha trajetória"
        ]},
        {"code": "D2", "name": "Coerência e Atitudes", "weight": 0.25, "questions": [
            "Passei a tomar decisões mais alinhadas aos meus valores",
            "Incorporei novos hábitos positivos após a EO.",
            "Encaro desafios com mais maturidade e consciência.",
            "Sinto maior coerência entre o que penso e o que faço."
        ]},
        {"code": "D3", "name": "Relações", "weight": 0.25, "questions": [
            "Tenho conseguido levar em consideração opiniões diferentes das minhas.",
            "Me comunico com mais clareza e respeito.",
            "Lido melhor com conflitos do que antes.",
            "Pessoas próximas perceberam mudanças positivas em mim."
        ]},
        {"code": "D4", "name": "Contribuição", "weight": 0.20, "questions": [
            "Passei a apoiar mais o desenvolvimento de outras pessoas.",
            "Compartilho os aprendizados da EO no meu cotidiano.",
            "Estou mais envolvido em iniciativas coletivas (no meu bairro, igreja, na minha comunidade de amigos, etc.)",
            "Acredito que minha mudança influencia outras pessoas"
        ]}
    ]
    
    # Notice the document says D4 is 20%, D3 is 25%.
    # If D4=0.2, D3=0.25, D1+D2 must be 0.55. Let's make D1=0.25, D2=0.30 to sum 1.0, or leave them. 
    # I'll set D1=0.25, D2=0.30 for exact 100%.
    dimensions_data[1]['weight'] = 0.30

    print("Populating dimensions and questions...")
    order = 1
    for d_data in dimensions_data:
        dim = ImpactDimension.objects.create(
            code=d_data['code'],
            name=d_data['name'],
            weight=d_data['weight']
        )
        for q_text in d_data['questions']:
            ImpactQuestion.objects.create(
                dimension=dim,
                text=q_text,
                order=order,
                is_open=False
            )
            order += 1

    # Open questions
    open_questions = [
        "Você poderia nos dizer qual mudança mais significativa você percebe em si mesmo desde o início da EO?",
        "E onde essa mudança aparece na prática no seu cotidiano? Poderia nos dar alguns exemplos?",
        "E para finalizar, como você acredita que estaria hoje se não tivesse participado da EO?"
    ]

    for q_text in open_questions:
        ImpactQuestion.objects.create(
            dimension=None,
            text=q_text,
            order=order,
            is_open=True
        )
        order += 1

    print("Done! Dimensions:", ImpactDimension.objects.count(), "Questions:", ImpactQuestion.objects.count())

if __name__ == '__main__':
    run()
