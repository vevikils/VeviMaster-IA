from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    is_pro = models.BooleanField(default=False)
    monthly_masterings_count = models.IntegerField(default=0)
    mastered_tracks_total = models.IntegerField(default=0)
    extra_credits = models.IntegerField(default=0)
    social_reward_claimed = models.BooleanField(default=False)
    last_reset_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Settings for {self.user.username}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField(max_length=500)
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True) # Podemos cambiar a False si quieres moderarlas

    def __str__(self):
        return f"Reseña de {self.user.username}"
