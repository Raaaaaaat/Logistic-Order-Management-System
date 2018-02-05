"""tmr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from order_management import views as tmr_views
urlpatterns = [
    path('admin/', admin.site.urls),

    #log_in part
    path('', tmr_views.log_in_index), #临时
    path('log_in/', tmr_views.log_in_index),
    path('ajax_log_in_check/', tmr_views.log_in_index, name='ajax_log_in_check'),

    #log_out_part
    path('ajax_log_out/', tmr_views.log_out_request, name='ajax_log_out'),

    #client part
    path('client/',             tmr_views.client_index,      name = 'client_index'),
    path('ajax_get_client/',    tmr_views.client_get_table_data,    name = 'ajax_get_client'),
    path('client_add/',         tmr_views.client_add,        name = 'client_add'),
    path('client_edit/',        tmr_views.client_edit,       name = 'client_edit'),
    path('ajax_edit_client/',   tmr_views.ope_edit_client,   name = 'ajax_edit_client'),
    path('ajax_delete_client/', tmr_views.ope_delete_client, name = 'ajax_delete_client'),
    path('get_client_options/', tmr_views.get_client_options,name = 'get_client_options'),

    #supplier part
    path('supplier/',             tmr_views.supplier_index,      name = 'supplier_index'),
    path('ajax_get_supplier/',    tmr_views.supplier_get_table_data,      name = 'ajax_get_supplier'),
    path('supplier_add/',         tmr_views.supplier_add,        name = 'supplier_add'),
    path('supplier_edit/',        tmr_views.supplier_edit,       name = 'supplier_edit'),
    path('ajax_edit_supplier/',   tmr_views.ope_edit_supplier,   name = 'ajax_edit_supplier'),
    path('ajax_delete_supplier/', tmr_views.ope_delete_supplier, name = 'ajax_delete_supplier'),
    path('get_supplier_options/', tmr_views.get_supplier_options,name = 'get_supplier_options'),
    path('get_sup_ope_options/',  tmr_views.get_sup_ope_options, name='get_sup_ope_options'),

    #order part
    path('order/',             tmr_views.order_index,      name = 'order_index'),
    path('order_add/',         tmr_views.order_add,        name = 'order_add'),
    path('ope_edit_order/',    tmr_views.ope_edit_order,   name='ope_edit_order'),
    path('order_detail/',      tmr_views.order_detail,     name='order_detail'),
]
