from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User


class ChatbotAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_chat_interaction(self):
        url = reverse("chat-interact")
        response = self.client.post(url, {"message": "Headache and fever"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recommendations", response.data)

    def test_session_history(self):
        # First create a chat interaction
        self.client.post(reverse("chat-interact"), {"message": "Test message"})

        # Check session list
        sessions_url = reverse("chat-session-list")
        response = self.client.get(sessions_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data[0]["messages"]), 2)  # User + bot messages
