from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator 
import uuid
from django_ckeditor_5.fields import CKEditor5Field

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
        ('POE', 'Panamá Oeste'),
    ]

    def profile_image_path(instance, filename):
        ext = filename.split('.')[-1]
        return f'profiles/user_{instance.user.id}_{uuid.uuid4()}.{ext}'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=10, choices=PROVINCES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    interests = models.JSONField(default=list, blank=True, null=True, help_text="Lista tus intereses como 'parkear', 'comer pio pio', 'escuchar plenas'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Blog(models.Model):
    def blog_image_path(instance, filename):
        ext = filename.split('.')[-1]
        return f'blogs/imageblog_{uuid.uuid4()}.{ext}'
    
    title = models.CharField(max_length=200)
    content = CKEditor5Field(null='true', blank='true', config_name='extends')
    image = models.ImageField(upload_to=blog_image_path, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def remove_image(self):
        if self.image:
            self.image.delete(save=False)
            self.image = None
            self.save()

class Review(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = CKEditor5Field(null='true', blank='true', config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.blog.title}"



class Comment(models.Model):
    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=False, help_text="El contenido del comentario no puede estar vacío.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter.username}"

    class Meta:
        ordering = ['-created_at']  # Ordenar comentarios por fecha de creación (más recientes primero)
    
class BlogStats(Blog):
    class Meta:
        proxy = True
        verbose_name = "Estadísticas del Blog"
        verbose_name_plural = "Estadísticas del Blog"