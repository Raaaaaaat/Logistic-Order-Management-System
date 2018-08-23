from django.db import models

# Create your models here.
class CLIENT(models.Model):
    No       = models.CharField(max_length=10, unique=True)
    type     = models.SmallIntegerField()  #0 = 公司客户， 1 = 个人客户
    co_name  = models.CharField(max_length=100, null=True)
    co_addr  = models.CharField(max_length=100, null=True)
    co_tel   = models.CharField(max_length=20,  null=True)
    tax_id   = models.CharField(max_length=100, null=True)
    account_owner  = models.CharField(max_length=50,  null=True)
    account_number = models.CharField(max_length=20,  null=True)
    account_bank   = models.CharField(max_length=100, null=True)
    contact_name   = models.CharField(max_length=100, null=True)
    contact_tel    = models.CharField(max_length=20,  null=True)
    contact_role   = models.CharField(max_length=100, null=True)
    contract_start = models.CharField(max_length=20,  null=True)
    contract_end   = models.CharField(max_length=20,  null=True)
    contract_file  = models.CharField(max_length=100, null=True)
    remark         = models.CharField(max_length=500, null=True)
    class Meta:
        permissions=(
            ("view_client",            "Can access information of client"),
            #("add_client",             "Can insert new client"),
            #("change_client",          "Can change normal info of client"),
            ("change_client_contract", "Can edit contract of client"),
            ("change_client_tax",      "Can edit tax_id of client"),
            #("delete_client",          "Can delete a client"),
        )

class SUPPLIER(models.Model):
    No       = models.CharField(max_length=10, unique=True)
    type     = models.SmallIntegerField()  #0 = 公司供应商， 1 = 个人供应商
    co_name  = models.CharField(max_length=100, null=True)
    co_addr  = models.CharField(max_length=100, null=True)
    co_tel   = models.CharField(max_length=20,  null=True)
    tax_id   = models.CharField(max_length=100, null=True)
    account_owner  = models.CharField(max_length=50,  null=True)
    account_number = models.CharField(max_length=20,  null=True)
    account_bank   = models.CharField(max_length=100, null=True)
    contact_name   = models.CharField(max_length=100, null=True)
    contact_tel    = models.CharField(max_length=20,  null=True)
    contact_role   = models.CharField(max_length=100, null=True)
    contract_start = models.CharField(max_length=20,  null=True)
    contract_end   = models.CharField(max_length=20,  null=True)
    contract_file  = models.CharField(max_length=100, null=True)
    remark         = models.CharField(max_length=500, null=True)
    class Meta:
        permissions=(
            ("view_supplier",            "Can access information of supplier"),
            #("add_supplier",             "Can insert new supplier"),
            #("change_supplier",          "Can change normal info of supplier"),
            ("change_supplier_contract", "Can edit contract of supplier"),
            ("change_supplier_tax",      "Can edit tax_id of supplier"),
            #("delete_supplier",          "Can delete a supplier"),
        )

class ORDER(models.Model):
    No        = models.CharField(max_length=12, unique=True)
    status    = models.SmallIntegerField() #6个状态 用数字代替
    client_id = models.IntegerField()
    dep_place = models.CharField(max_length=200, null=True)
    dep_city  = models.CharField(max_length=50)
    des_place = models.CharField(max_length=200, null=True)
    des_city  = models.CharField(max_length=50)
    rec_name  = models.CharField(max_length=50, default="")
    rec_tel   = models.CharField(max_length=50, default="")
    cargo_name     = models.CharField(max_length=100)
    cargo_weight   = models.FloatField(max_length=100, null=True)
    cargo_quantity = models.CharField(max_length=50, null=True)
    cargo_size     = models.FloatField(max_length=100, null=True)
    remark         = models.CharField(max_length=500, null=True)
    create_time    = models.DateTimeField(auto_now_add=True)
    pick_up_time   = models.DateTimeField(null=True)
    delivery_time  = models.DateTimeField(null=True)
    if_close       = models.SmallIntegerField(null=True) #2018 7 16新增，用来标记结账
    if_delete      = models.SmallIntegerField()
    class Meta:
        permissions = (
            ("view_order", "Can access information of orders"),
            ("view_trash_order", "Can access information of orders dropped"),
            ("view_order_finance", "Can access information of financal certer"),
            ("view_data_center", "Can access information of data certer"),
            ("edit_order_create_time","edit create time of order objects"),
            ("close_order", "针对订单的结账操作，以及反结账操作"),

            # ("add_order",
            # ("change_order",
            # ("delete_order",
        )
        ordering = ['-id']

class SUP_STEP(models.Model): #供应商操作环节的列表
    name = models.CharField(max_length=100)

class PAYABLES(models.Model):
    status      = models.SmallIntegerField() #0 未核销 1:已核销
    order_id    = models.IntegerField()
    step        = models.IntegerField()     #环节主码
    description = models.CharField(max_length=200, null=True)
    supplier_id = models.IntegerField()
    payables    = models.FloatField(null=True)
    paid_cash   = models.FloatField(null=True)
    paid_oil    = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    clear_time  = models.DateTimeField(null=True)
    invoice     = models.CharField(max_length=200, null=True, default="")
    remark      = models.CharField(max_length=500, null=True)
    if_close = models.SmallIntegerField(null=True)
    class Meta:
        permissions = (
            ("paya_manage", "Can manage(add/change/delete) payables"),
            ("paya_invoice","Can manage(add/change/delete) payables invoice"),
            ("paya_verify", "Can verify and unverify payables"),
        )


class RECEIVEABLES(models.Model):
    status      = models.SmallIntegerField()
    order_id    = models.IntegerField()
    step        = models.IntegerField(null=True)
    description = models.CharField(max_length=200)
    receiveables= models.FloatField(null=True)
    received    = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    clear_time  = models.DateTimeField(null=True)
    invoice     = models.IntegerField(null=True)
    remark      = models.CharField(max_length=500, null=True)
    if_close = models.SmallIntegerField(null=True)
    class Meta:
        permissions = (
            ("recv_manage",  "Can manage(add/change/delete) receiveables"),
            ("recv_invoice", "Can view list of receiveables invoice"),#打开票务管理的权限
            ("recv_verify",  "Can verify and unverify receiveables"),
        )


class LOG_TRACE(models.Model):
    order_id = models.IntegerField()
    status = models.CharField(max_length=50)
    select_time   = models.DateTimeField(null=True)
    create_time   = models.DateTimeField()
    create_user   = models.CharField(max_length=100, null=True)
    desc   = models.CharField(max_length=50, null=True) #描述


class RECV_INVOICE(models.Model):
    invoice     = models.CharField(max_length=100)
    client_id   = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    remark      = models.CharField(max_length=100, null=True)
    create_user = models.CharField(max_length=100)

class OPERATE_LOG(models.Model):
    time   = models.DateTimeField(auto_now_add=True)
    user   = models.CharField(max_length=50)
    field  = models.CharField(max_length=50)
    detail = models.CharField(max_length=500, null=True)
    class Meta:
        permissions = (
            ("view_operate_log", "can view operate log"),
        )
        ordering = ['-id']

class EDIT_PRICE_REQUEST(models.Model): #只有对于上一个月以及之前的订单才需要进入这个表
    time         = models.DateTimeField(auto_now_add=True)
    user         = models.CharField(max_length=50)
    type         = models.CharField(max_length=20) #recv 或者paya代表修改这个而价格，或者recv_delete或者paya_delete
    target_id    = models.IntegerField() #分录在各自表中的主码
    target_price = models.FloatField()
    class Meta:
        permissions = (
            ("handle_edit_price_request", "can accept or refuse request asking to edit price"),
        )
        ordering = ['-id']