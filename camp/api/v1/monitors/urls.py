from django.urls import include, path

from . import endpoints

app_name = 'monitors'

urlpatterns = [
    path('', endpoints.MonitorList.as_view(), name='monitor-list'),
    path('<monitor_id>/', endpoints.MonitorDetail.as_view(), name='monitor-detail'),
    path('<monitor_id>/entries/', endpoints.EntryList.as_view(), name='entry-list'),
    path('<monitor_id>/entries/csv/', endpoints.EntryCSV.as_view(), name='entry-csv'),
]
