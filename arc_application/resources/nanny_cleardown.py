from ..models.arc import Arc


def run(*args):
    Arc.objects.filter(app_type='Nanny').delete()
