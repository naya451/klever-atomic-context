from django.conf.urls import url
from users import views


urlpatterns = [
    url(r'^signin/$', views.user_signin, name='login'),
    url(r'^signout/$', views.user_signout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^edit/$', views.edit_profile, name='edit_profile'),
    url(r'^profile/(?P<user_id>[0-9]+)$', views.show_profile, name='show_profile')
]
