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
            ("view_client",            "允许查看客户的信息 "),
            #("add_client",             "Can insert new client"),
            #("change_client",          "Can change normal info of client"),
            ("change_client_contract", "允许更改客户的合同信息 "),
            ("change_client_tax",      "允许变更客户的税号 "),
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
            ("view_supplier",            "允许查看供应商的信息"),
            #("change_supplier",          "Can change normal info of supplier"),
            ("change_supplier_contract", "允许更改供应商的合同信息"),
            ("change_supplier_tax",      "允许变更供应商的税号"),
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
            ("view_order", "允许查看订单的基本信息"),
            ("view_trash_order", "允许查看被废弃订单的历史信息"),
            ("view_order_finance", "允许进入财务中心"),
            ("view_data_center", "允许进入数据中心"),
            ("edit_order_create_time","允许编辑订单的下单时间"),
            ("close_order", "针对订单的关闭操作"),
            ("open_order", "针对订单的打开操作,用于取消关闭订单的效果"),
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
    client_id   = models.IntegerField(null=True)
    step        = models.IntegerField()     #环节主码
    description = models.CharField(max_length=200, null=True)
    supplier_id = models.IntegerField()
    payables    = models.FloatField(null=True)
    paid_cash   = models.FloatField(null=True)
    paid_oil    = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    clear_time  = models.DateTimeField(null=True)
    invoice     = models.CharField(max_length=200, null=True, default="")
    #remark      = models.CharField(max_length=500, null=True)
    pay_log     = models.CharField(max_length=500, null=True, default="") #增加于2019 4 21，用于记录核销操作的时间
    if_close    = models.SmallIntegerField(null=True)
    class Meta:
        permissions = (
            ("paya_manage", "可以查看以及操作应付账款条目"),
            ("paya_invoice","可以对应付账款的进行开票操作"),
            ("paya_verify", "可以对应付账款进行核销操作"),
        )


class RECEIVEABLES(models.Model):
    status      = models.SmallIntegerField() #沒啥用？
    order_id    = models.IntegerField()
    client_id   = models.IntegerField(null=True)
    step        = models.IntegerField(null=True)
    description = models.CharField(max_length=200)
    receiveables= models.FloatField(null=True)
    received    = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    clear_time  = models.DateTimeField(null=True)
    invoice     = models.IntegerField(null=True)
    #remark      = models.CharField(max_length=500, null=True)
    if_close = models.SmallIntegerField(null=True)
    class Meta:
        permissions = (
            ("recv_manage",  "可以查看以及操作应收账款条目"),
            ("recv_invoice", "可以对应收账款的进行开票操作以及进行票务管理"),#打开票务管理的权限
            ("recv_verify",  "可以对应收账款进行核销操作"),
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
            ("view_operate_log", "允许查看所有的操作日志"),
        )
        ordering = ['-id']

class EDIT_PRICE_REQUEST(models.Model): #只有对于上一个月以及之前的订单才需要进入这个表
    time         = models.DateTimeField(auto_now_add=True)
    user         = models.CharField(max_length=50)
    type         = models.CharField(max_length=20) #recv 或者paya代表修改这个而价格，或者recv_delete或者paya_delete，或者recv_add,paya_add
    target_id    = models.IntegerField() #分录在各自表中的主码, 如果爲新增模式，则代表order的id
    target_price = models.FloatField()
    add_desc     = models.CharField(max_length=200, null=True) #新增专用，新增的分录的描述 以下新增于2019 4 15
    add_step     = models.IntegerField(null=True)              #新增专用，环节编码
    add_cs_id    = models.IntegerField(null=True)              #新增专用，对应供应商或者客户的id
    class Meta:
        permissions = (
            ("handle_edit_price_request", "可以接受或者拒绝对于订单应收应付分录增加、修改、删除的请求"),
        )
        ordering = ['-id']

class USER_FEEDBACK(models.Model):
    time        = models.DateTimeField(auto_now_add=True)
    user        = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True)