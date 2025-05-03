from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


# MODELOS
class UserProfile(models.Model):
    PROVINCES = [
        ('BOC', 'Bocas del Toro'),
        ('CHI', 'Chiriquí'),
        ('COC', 'Coclé'),
        ('COL', 'Colón'),
        ('DAR', 'Darién'),
        ('HER', 'Herrera'),
        ('LOS', 'Los Santos'),
        ('PAN', 'Panamá'),
        ('VER', 'Veraguas'),
        ('PAN_OESTE', 'Panamá Oeste'),
    ]

    def profile_image_path(instance, filename):
        ext = filename.split('.')[-1]
        return f'profiles/user_{instance.user.id}_{uuid.uuid4()}.{ext}'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=10, choices=PROVINCES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Blog(models.Model):
    def blog_image_path(instance, filename):
        ext = filename.split('.')[-1]
        return f'blogs/imageblog_{uuid.uuid4()}.{ext}'

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to=blog_image_path, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.blog.title}"



class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter.username}"