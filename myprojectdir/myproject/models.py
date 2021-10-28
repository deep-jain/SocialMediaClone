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


#PLEASE MIGRATE TO ADD THIS TABLE TO DATABASE!
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    content = models.TextField(max_length=1000, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def send_message(from_user, to_user, content):
        sender_message = Message(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            content=content)
        sender_message.save()

        recipient_message = Message(
            user=to_user,
            sender=from_user,
            content=content,
            recipient=from_user)
        recipient_message.save()

        return sender_message

    def get_messages(user):
        users = []
        messages = Message.objects.filter(user=user).values('recipient').annotate(last=Max('date')).order_by('-last')
        for message in messages:
            users.append({
                'user':User.objects.get(pk=message['recipient']),
                'last': message['last'],
            })
        return users