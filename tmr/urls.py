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
    path('get_sup_step_options/', tmr_views.get_sup_step_options,name = 'get_sup_step_options'),

    #order part
    path('order/',             tmr_views.order_index,      name = 'order_index'),
    path('order_add/',         tmr_views.order_add,        name = 'order_add'),
    path('ope_edit_order/',    tmr_views.ope_edit_order,   name='ope_edit_order'),
    path('order_detail/',      tmr_views.order_detail,     name='order_detail'),
    path('ope_add_trace/',     tmr_views.ope_add_trace,    name='ope_add_trace'),
    path('get_trace_data/',    tmr_views.get_trace_data,   name='get_trace_data'),
    path('ope_edit_trace/',    tmr_views.ope_edit_trace,   name='ope_edit_trace'),

    #price part
    path('price_management/',           tmr_views.index_price,               name='price_management'),
    path('get_receiveables/',           tmr_views.get_receiveables,          name='get_receiveables'),
    path('add_receiveables/',           tmr_views.add_receiveables,          name='add_receiveables'),
    path('update_receiveables_desc/',   tmr_views.update_receiveables_desc,  name='update_receiveables_desc'),
    path('update_receiveables_price/',  tmr_views.update_receiveables_price, name='update_receiveables_price'),
    path('delete_receiveables/',        tmr_views.delete_receiveables,       name='delete_receiveables'),

    path('get_payables/',           tmr_views.get_payables,          name='get_payables'),
    path('add_payables/',           tmr_views.add_payables,          name='add_payables'),
    path('update_payables_info/',   tmr_views.update_payables_info,  name='update_payables_info'),
    path('update_payables_price/',  tmr_views.update_payables_price, name='update_payables_price'),
    path('delete_payables/',        tmr_views.delete_payables,       name='delete_payables'),
]
