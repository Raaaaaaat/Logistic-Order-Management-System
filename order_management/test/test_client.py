from django.test import TestCase
from order_management.models import CLIENT

class ClientTestCase(TestCase):
    def setUp(self):
        CLIENT.objects.create(No="C213", co_name="roar")

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        c = CLIENT.objects.get(No="C213")
        self.assertEqual(c.co_name, 'roar')
