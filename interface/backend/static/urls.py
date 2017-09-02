from django.conf.urls import url
from . import views

urlpatterns = (
    url(r'^$', views.open_image, name='open_image'),
    url(r'^detect$', views.detect_and_select, name='detect_and_select'),
    url(r'^annotate$', views.annotate_and_segment, name='annotate_and_segment'),
    url(r'^report$', views.report_and_export, name='report_and_export'),

)
