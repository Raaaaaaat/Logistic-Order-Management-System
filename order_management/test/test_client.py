from django.test import TestCase
from order_management.models import CLIENT
from django.contrib.auth.models import UserManager,User, Permission
from django.test import Client

class ClientTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username="test",password="test")

    def test_client(self):
        user = User.objects.get(username="test")
        perm = Permission.objects.get(codename='add_client')
        user.user_permissions.add(perm)
        http_client = Client()
        a = http_client.login(username='test', password='test')
        resp = http_client.post("/ajax_edit_client/",{
            "if_edit":"0",
            "type":"1",
            "contact_name":"horace",
            "contact_tel":"911"})

        c = CLIENT.objects.get(No="C001")
        self.assertEqual(c.contact_name, 'horace')
