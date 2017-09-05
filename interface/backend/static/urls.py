from django.conf.urls import url
from . import views

urlpatterns = (
    url(r'^$', views.open_image, name='open-image'),
    url(r'^detect$', views.detect_and_select, name='detect-and-select'),
    url(r'^annotate$', views.annotate_and_segment, name='annotate-and-segment'),
    url(r'^report$', views.report_and_export, name='report-and-export'),

)
