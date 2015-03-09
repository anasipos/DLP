from views import ChooseTestView, CreateUserTest, TakeTestView, TestResults

__author__ = 'anamaria.sipos'

from django.conf.urls import url, patterns

urlpatterns = patterns('',
                       url(r'^page/(?P<pk>\d+)/$', TakeTestView.as_view(), name='user-page'),
                       url(r'^(?P<test_id>\d+)/$', CreateUserTest.as_view(), name='start-test'),
                       url(r'^(?P<pk>\d+)/results/$', TestResults.as_view(), name='results'),
                       url(r'^$', ChooseTestView.as_view(), name='test-list'),

)

