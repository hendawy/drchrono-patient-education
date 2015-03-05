from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', 'sharebackend.views.home', name='home'),
    url(r'^patients/$', 'sharebackend.views.list_patients',
        name='list_patients'),
    url(r'^group/new/$', 'sharebackend.views.new_group',
        name='new_group'),
    url(r'^group/share/$', 'sharebackend.views.file_share',
        name='file_share'),
    url(r'^group/(?P<tag_text>\w+)/$', 'sharebackend.views.get_group',
        name='get_group'),

    # url(r'^sharebackend/', include('pshare.sharebackend.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
