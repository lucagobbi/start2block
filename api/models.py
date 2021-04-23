from django.db import models
from django.contrib.auth.models import User
from .utils import sendTransaction
import hashlib

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    datetime = models.DateTimeField(auto_now_add=True)
    content = models.TextField(default=None)
    hash = models.CharField(max_length=32, default=None, null=True)
    txId = models.CharField(max_length=66, default=None, null=True)

    def __str__(self):
        return self.content

    def get_last_posts(self):
        return Post.objects.all().order_by("-datetime")

    def writeOnChain(self):
        self.hash = hashlib.sha256(self.content.encode('utf-8')).hexdigest()
        self.txId = sendTransaction(self.hash)
        self.save()

# model to track last user's IP address
class UserIP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_ip_address = models.CharField(max_length=50)

    def __str__(self):
        return self.last_ip_address