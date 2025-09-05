from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
import os
from .models import InstagramPost

# NAPOMENA: Logika ispod pretpostavlja da 'session.json' datoteka postoji i da je ažurna,
# što se postiže redovitim pokretanjem 'fetch_instagram_posts' komande.
# Kredencijali su ovdje tvrdo kodirani kako bi odgovarali stilu management komande.
# Preporučuje se njihovo premještanje u settings.py.
INSTAGRAM_USERNAME = 'goczg'
INSTAGRAM_PASSWORD = 'J4kazapork@'

@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    # Dodan 'has_content_display' za prikaz u gridu
    list_display = ('instagram_id', 'publish_date', 'like_count', 'comment_count', 'published', 'image_preview_list', 'has_content_display')
    list_filter = ('published', 'publish_date')
    search_fields = ('instagram_id', 'content')
    list_editable = ('published',)
    
    # 'content' je uklonjen iz readonly_fields kako bi se omogućilo uređivanje.
    # Dodan 'post_actions' za prikaz gumba.
    readonly_fields = (
        'instagram_id', 'post_url', 'publish_date', 'post_song', 
        'like_count', 'comment_count', 'image_preview_item', 'post_actions'
    )
    
    fieldsets = (
        ('Status', {
            'fields': ('published',)
        }),
        ('Informacije o objavi', {
            'fields': ('instagram_id', 'post_url', 'publish_date', 'like_count', 'comment_count')
        }),
        ('Sadržaj (uređivanje ovog polja će promijeniti opis na Instagramu)', {
            'fields': ('content', 'post_song', 'image_preview_item')
        }),
        ('Akcije', {
            'fields': ('post_actions',)
        }),
    )

    def image_preview_list(self, obj):
        if obj.post_image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="height: 60px; width: auto;" /></a>', obj.post_image.url)
        return "Nema slike"
    image_preview_list.short_description = 'Slika'

    def image_preview_item(self, obj):
        if obj.post_image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height: 300px; max-width: 300px;" /></a>', obj.post_image.url)
        return "Nema slike"
    image_preview_item.short_description = 'Pregled slike'

    def has_content_display(self, obj):
        """Vraća True ako objava ima tekstualni sadržaj, za prikaz u admin listi."""
        return bool(obj.content and obj.content.strip())
    has_content_display.boolean = True
    has_content_display.short_description = 'Ima teksta'

    # --- Logika za custom gumb i akciju ---

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/publish-on-ig/',
                self.admin_site.admin_view(self.publish_on_ig_view),
                name='instagram_instagrampost_publish_on_ig',
            ),
        ]
        return custom_urls + urls

    def post_actions(self, obj):
        """Prikazuje gumb u formi za uređivanje koji pokreće custom akciju."""
        if obj.pk:
            publish_url = reverse('admin:instagram_instagrampost_publish_on_ig', args=[obj.pk])
            return format_html('<a class="button" href="{}">Pošalji na IG</a>', publish_url)
        return "—"
    post_actions.short_description = 'Objavi izmjene'
    
    def publish_on_ig_view(self, request, object_id, *args, **kwargs):
        """
        Admin view koji upravlja logikom za uređivanje opisa objave na Instagramu.
        """
        post = self.get_object(request, object_id)
        
        redirect_url = reverse(
            'admin:instagram_instagrampost_change',
            args=[post.pk],
            current_app=self.admin_site.name,
        )

        try:
            cl = Client()
            session_file = "session.json"
            if not os.path.exists(session_file):
                self.message_user(request, "Datoteka sesije 'session.json' nije pronađena. Pokrenite 'fetch_instagram_posts' komandu.", messages.ERROR)
                return HttpResponseRedirect(redirect_url)

            cl.load_settings(session_file)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

            media_id = cl.media_id(post.instagram_id)
            new_caption = post.content if post.content else ""
            
            cl.media_edit(media_id, new_caption)
            
            post.published = True
            post.save()
            
            self.message_user(request, "Opis objave je uspješno ažuriran na Instagramu.", messages.SUCCESS)
        
        except LoginRequired:
             self.message_user(request, "Instagram sesija je istekla. Pokrenite 'fetch_instagram_posts' komandu kako biste je osvježili.", messages.ERROR)
        except ClientError as e:
            self.message_user(request, f"Greška prilikom komunikacije s Instagram API-jem: {e}", messages.ERROR)
        except Exception as e:
            self.message_user(request, f"Dogodila se neočekivana greška: {e}", messages.ERROR)
            
        return HttpResponseRedirect(redirect_url)