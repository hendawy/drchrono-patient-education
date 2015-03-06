from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'sharebackend.views.home', name='home'),
    url(r'^patients/$', 'sharebackend.views.list_patients',
        name='list_patients'),
    url(r'^group/add/new/$', 'sharebackend.views.new_group',
        name='new_group'),
    url(r'^group/file/share/$', 'sharebackend.views.file_share',
        name='file_share'),
    url(r'^group/(?P<tag_text>\w+)/$', 'sharebackend.views.get_group',
        name='get_group'),
    url(r'^group/remove/(?P<tag_text>\w+)/$', 'sharebackend.views.remove_group',
        name='remove_group'),
    url(r'^group/$', 'sharebackend.views.list_groups',
        name='list_groups'),
    url(r'^files/$', 'sharebackend.views.list_files',
        name='list_files'),
    url(r'^file/(?P<file_id>[0-9]+)/$', 'sharebackend.views.get_file',
        name='get_file'),
    url(r'^resource/test/$', 'sharebackend.views.test_resources',
        name='test_resources'),
    url(r'^landing/$', 'sharebackend.views.landing',
        name='landing'),
    url(r'^logout/$', 'sharebackend.views.logout_view',
        name='logout'),
)
