from django.shortcuts import render

# Create your views here.

from order_management.user_views.log_in_index import *
from order_management.user_views.log_out import *

from order_management.views_client.client_index import *
from order_management.views_client.client_get_table_data import *
from order_management.views_client.client_add import *
from order_management.views_client.client_edit import *
from order_management.views_client.ope_delete_client import *
from order_management.views_client.ope_edit_client import *
from order_management.views_client.get_client_options import *

from order_management.views_supplier.supplier_index import *
from order_management.views_supplier.supplier_get_table_data import *
from order_management.views_supplier.supplier_add import *
from order_management.views_supplier.supplier_edit import *
from order_management.views_supplier.ope_delete_supplier import *
from order_management.views_supplier.ope_edit_supplier import *

from order_management.views_order.order_index import *
from order_management.views_order.order_add import *
from order_management.views_order.order_edit import *
from order_management.views_order.ope_edit_order import *