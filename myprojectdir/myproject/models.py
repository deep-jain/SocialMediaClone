from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Max

class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    media = models.URLField()
    censor = models.BooleanField(default=False)
    content = models.TextField()
    slug = models.SlugField(unique=True, max_length=255)
    spotifyLink = models.URLField(blank=True)
    embedSpotifyLink = models.CharField(blank=True, max_length=255)


    def get_absolute_url(self):
        return reverse('user_post_detail', args[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ['created_on']

        def __unicode__(self):
            return self.title

class Comment(models.Model):
    author_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

class Conversations(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2")

class Message(models.Model):
    convo_id = models.ForeignKey(Conversations, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    content = models.TextField(max_length=1000, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

class suscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suscriptions = models.TextField(max_length=10000, blank=True)