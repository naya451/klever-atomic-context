from django.utils.translation import ugettext as _, activate
from urllib.parse import unquote
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Omega.populate import Population
from Omega.vars import ERRORS


def omega_error(request, err_code=0, user_message=None):
    if request.user.is_authenticated():
        activate(request.user.extended.language)
    else:
        activate(request.LANGUAGE_CODE)

    err_code = int(err_code)

    back = None
    if request.method == 'GET':
        back = request.GET.get('back', None)
        if back is not None:
            back = unquote(back)

    if isinstance(user_message, str):
        message = user_message
    else:
        if err_code in ERRORS:
            message = ERRORS[err_code]
        else:
            message = _('Unknown error')

    return render(request, 'error.html', {'message': message, 'back': back})


@login_required
def population(request):
    if request.method == 'POST':
        username, password = Population(request.user).full_population()
        return render(request, 'Population.html',
                      {'password': password, 'username': username})
    return render(request, 'Population.html', {})
