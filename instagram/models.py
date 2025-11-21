from django.db import models

class InstagramPost(models.Model):
    instagram_id = models.CharField(max_length=255, unique=True, verbose_name="Instagram ID (Code)")
    instagram_pk = models.CharField(max_length=255, unique=True, verbose_name="Instagram PK", null=True, blank=True)
    content = models.TextField(blank=True, null=True, verbose_name="Opis")
    post_url = models.URLField(max_length=500, blank=True, verbose_name="URL objave")
    post_image = models.FileField(upload_to='IG/', max_length=512, blank=True, verbose_name="Slika")
    publish_date = models.DateTimeField(null=True, blank=True, verbose_name="Datum objave")
    published = models.BooleanField(default=False, verbose_name="Objavljeno")
    post_song = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pjesma")

    class Meta:
        ordering = ['-publish_date']
        verbose_name = "Instagram objava"
        verbose_name_plural = "Instagram objave"

    def __str__(self):
        return f"Objava {self.instagram_id} od {self.publish_date.strftime('%Y-%m-%d') if self.publish_date else 'N/A'}"

class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Naziv")
    class Meta:
        ordering = ['name']
        verbose_name = "Hashtag"
        verbose_name_plural = "Hashtagovi"

    def __str__(self):
        return self.name

class HashtagInsight(models.Model):
    post = models.ForeignKey(InstagramPost, on_delete=models.CASCADE, related_name='hashtag_insights', verbose_name="Objava")
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='insights', verbose_name="Hashtag")
    count = models.IntegerField(default=0, verbose_name="Broj impresija")

    class Meta:
        ordering = ['-count']
        verbose_name = "Statistika hashtaga"
        verbose_name_plural = "Statistike hashtagova"
        unique_together = ('post', 'hashtag')

    def __str__(self):
        return f"Statistika za {self.hashtag.name} na objavi {self.post.instagram_id}"

class Impression(models.Model):
    post = models.ForeignKey(InstagramPost, on_delete=models.CASCADE, related_name='impressions', verbose_name="Objava")
    name = models.CharField(max_length=100, verbose_name="Izvor") # e.g., FEED, PROFILE, HASHTAG
    value = models.PositiveIntegerField(default=0, verbose_name="Vrijednost")

    class Meta:
        ordering = ['-value']
        verbose_name = "Impresija po izvoru"
        verbose_name_plural = "Impresije po izvoru"
        unique_together = ('post', 'name')

    def __str__(self):
        return f"{self.name}: {self.value} for post {self.post.instagram_id}"


class ContentInsight(models.Model):
    post = models.ForeignKey(InstagramPost, on_delete=models.CASCADE, related_name='insights', verbose_name="Objava")
    
    likes = models.IntegerField(default=0, verbose_name="Lajkovi")
    comments = models.IntegerField(default=0, verbose_name="Komentari")
    reach = models.IntegerField(default=0, verbose_name="Doseg")
    impressions = models.IntegerField(default=0, verbose_name="Impresije")
    saved = models.IntegerField(default=0, verbose_name="Spremanja")
    shares = models.IntegerField(default=0, null=True, blank=True, verbose_name="Dijeljenja")
    profile_visits = models.IntegerField(default=0, verbose_name="Posjete profilu")

    fetched_at = models.DateTimeField(auto_now_add=True, verbose_name="Dohvaćeno")

    class Meta:
        ordering = ['-fetched_at']
        verbose_name = "Statistika objave"
        verbose_name_plural = "Statistike objava"
        get_latest_by = "fetched_at"

    def __str__(self):
        return f"Statistika za {self.post.instagram_id} @ {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"

class AccountInsight(models.Model):
    profile_visits = models.PositiveIntegerField(default=0, verbose_name="Posjete profilu")
    followers_delta_from_last_week = models.IntegerField(default=0, verbose_name="Promjena pratitelja (tjedan)")
    gender_graph = models.JSONField(default=dict, verbose_name="Graf po spolu")
    all_followers_age_graph = models.JSONField(default=dict, verbose_name="Graf po dobi (svi)")
    followers_top_cities_graph = models.JSONField(default=dict, verbose_name="Top gradovi pratitelja")
    followers_top_countries_graph = models.JSONField(default=dict, verbose_name="Top države pratitelja")
    week_daily_followers_graph = models.JSONField(default=dict, verbose_name="Dnevni broj pratitelja (tjedan)")
    impressions = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="Impresije")
    reach = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="Doseg")
    fetched_at = models.DateTimeField(auto_now_add=True, verbose_name="Dohvaćeno")
    
    class Meta:
        ordering = ['-fetched_at']
        verbose_name = "Statistika računa"
        verbose_name_plural = "Statistike računa"
        
    def __str__(self):
        return f"Statistika računa @ {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"

class Following(models.Model):
    instagram_id = models.TextField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    fullname = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    should_unfollow = models.BooleanField(default=False, verbose_name="unfollow")
    should_follow = models.BooleanField(default=False, verbose_name="Ofollow")
