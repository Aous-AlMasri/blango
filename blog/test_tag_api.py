from django.test import LiveServerTestCase
from requests.auth import HTTPBasicAuth
from rest_framework.test import RequestsClient

from django.contrib.auth import get_user_model
from blog.models import Tag


class TagApiTestCase(LiveServerTestCase):
  def setUp(self):
    get_user_model().objects.create_user(
      email="test@gmail.com", password="password"
    )

    self.tags = {"tag1", "tag2", "tag3"}
    for tag in self.tags:
      Tag.objects.create(value=tag)
    self.client = RequestsClient()
  
  def test_tag_list(self):
    resp = self.client.get(self.live_server_url + "/api/v1/tags/")
    self.assertEqual(resp.status_code, 200)
    data = resp.json()["results"]
    self.assertEqual(len(data), 3)
    self.assertEqual(self.tags, {t["value"] for t in data})

  def test_tag_create_basic_auth(self):
    self.client.auth = HTTPBasicAuth("test@gmail.com", "password")
    resp = self.client.post(self.live_server_url + "/api/v1/tags/", {"value": "tag4"})
    self.assertEqual(resp.status_code, 201)
    self.assertEqual(Tag.objects.all().count(), 4)
  
  def test_tag_create_token_auth(self):
    token_resp = self.client.post(
      self.live_server_url + "/api/v1/token-auth/",
      {"username": "test@gmail.com", "password": "password"}
    )
    self.client.headers["Authorization"] = "Token " + token_resp.json()["token"]

    resp = self.client.post(self.live_server_url + "/api/v1/tags/", {"value": "tag4"})
    self.assertEqual(resp.status_code, 201)
    self.assertEqual(Tag.objects.all().count(), 4)
