from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
import os
from .models import InstagramPost, ContentInsight, AccountInsight, Hashtag, HashtagInsight, Impression

# Ensure INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD are set in your settings.py
INSTAGRAM_USERNAME = getattr(settings, "INSTAGRAM_USERNAME", None)
INSTAGRAM_PASSWORD = getattr(settings, "INSTAGRAM_PASSWORD", None)


class ContentInsightInline(admin.TabularInline):
    model = ContentInsight
    fields = ('fetched_at', 'likes', 'comments', 'reach', 'impressions', 'saved', 'profile_visits')
    readonly_fields = fields
    can_delete = False
    extra = 0
    ordering = ('-fetched_at',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = (
        'instagram_id', 'publish_date', 'latest_likes', 'latest_reach',
        'impressions_diff', 'likes_diff', 'published', 'image_preview_list', 'has_content_display'
    )
    list_filter = ('published', 'publish_date')
    search_fields = ('instagram_id', 'content')
    list_editable = ('published',)

    readonly_fields = (
        'instagram_id', 'instagram_pk', 'post_url', 'publish_date', 'post_song',
        'image_preview_item', 'post_actions'
    )

    fieldsets = (
        ('Status', {'fields': ('published',)}),
        ('Informacije o objavi', {'fields': ('instagram_id', 'instagram_pk', 'post_url', 'publish_date')}),
        ('Sadržaj (uređivanje ovog polja će promijeniti opis na Instagramu)',
         {'fields': ('content', 'post_song', 'image_preview_item')}),
        ('Akcije', {'fields': ('post_actions',)})
    )

    inlines = [ContentInsightInline]

    def get_queryset(self, request):
        """
        Pre-dohvaćamo sve povezane insighte kako bismo izbjegli
        dodatne upite na bazu za svaki red u listi.
        """
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('insights')
        return qs

    def image_preview_list(self, obj):
        if obj.post_image and hasattr(obj.post_image, 'url'):
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="height: 60px; width: auto;" /></a>',
                               obj.post_image.url)
        return "Nema slike"

    image_preview_list.short_description = 'Slika'

    def image_preview_item(self, obj):
        if obj.post_image and hasattr(obj.post_image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" style="max-height: 300px; max-width: 300px;" /></a>',
                obj.post_image.url)
        return "Nema slike"

    image_preview_item.short_description = 'Pregled slike'

    def has_content_display(self, obj):
        return bool(obj.content and obj.content.strip())

    has_content_display.boolean = True
    has_content_display.short_description = 'Ima teksta'

    def latest_likes(self, obj):
        latest_insight = next(iter(obj.insights.all()), None)
        return latest_insight.likes if latest_insight else 'N/A'

    latest_likes.short_description = 'Lajkovi (zadnji)'

    def latest_reach(self, obj):
        latest_insight = next(iter(obj.insights.all()), None)
        return latest_insight.reach if latest_insight else 'N/A'

    latest_reach.short_description = 'Doseg (zadnji)'

    def impressions_diff(self, obj):
        """
        Prikazuje razliku u impresijama u lijepom HTML formatu.
        """
        # Koristimo list() da evaluiramo queryset koji je već u memoriji
        insights = list(obj.insights.all()[:2])

        if len(insights) < 2:
            return "N/A"

        latest_insight = insights[0]
        previous_insight = insights[1]

        diff = latest_insight.impressions - previous_insight.impressions

        if diff == 0:
            return 0
        else:
            return diff

    def _impressions_diff_for_ordering(self, obj):
        """
        Skrivena metoda koja vraća samo broj za potrebe sortiranja.
        """
        insights = list(obj.insights.all()[:2])
        if len(insights) < 2:
            return 0  # Vraćamo 0 (ili None) za postove bez dovoljno podataka
        return insights[0].impressions - insights[1].impressions

    impressions_diff.admin_order_field = '_impressions_diff_for_ordering'
    impressions_diff.short_description = 'Impresije (diff)'

    def likes_diff(self, obj):
        """
        Prikazuje razliku u lajkovima u lijepom HTML formatu.
        """
        insights = list(obj.insights.all()[:2])

        if len(insights) < 2:
            return "N/A"

        latest_insight = insights[0]
        previous_insight = insights[1]

        # Jedina promjena je ovdje: .likes umjesto .impressions
        diff = latest_insight.likes - previous_insight.likes

        if diff == 0:
            return 0
        else:
            return diff

    def _likes_diff_for_ordering(self, obj):
        """
        Skrivena metoda koja vraća samo broj za potrebe sortiranja.
        """
        insights = list(obj.insights.all()[:2])
        if len(insights) < 2:
            return 0
        # I ovdje: .likes umjesto .impressions
        return insights[0].likes - insights[1].likes

    # Povezujemo prikaznu metodu sa skrivenom metodom za sortiranje
    likes_diff.admin_order_field = '_likes_diff_for_ordering'
    likes_diff.short_description = 'Lajkovi (diff)'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/publish-on-ig/', self.admin_site.admin_view(self.publish_on_ig_view),
                 name='instagram_instagrampost_publish_on_ig'),
        ]
        return custom_urls + urls

    def post_actions(self, obj):
        if obj.pk:
            publish_url = reverse('admin:instagram_instagrampost_publish_on_ig', args=[obj.pk])
            return format_html('<a class="button" href="{}">Pošalji na IG</a>', publish_url)
        return "—"

    post_actions.short_description = 'Objavi izmjene'

    def publish_on_ig_view(self, request, object_id, *args, **kwargs):
        post = self.get_object(request, object_id)
        # Ispravljen redirect URL da koristi ispravan namespace
        redirect_url = reverse('admin:instagram_instagrampost_change', args=[post.pk])

        if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
            self.message_user(request, "INSTAGRAM_USERNAME i INSTAGRAM_PASSWORD nisu postavljeni u settings.py.",
                              messages.ERROR)
            return HttpResponseRedirect(redirect_url)

        try:
            # TODO::implement service.py login
            cl = Client()
            session_file = "session.json"
            if not os.path.exists(session_file):
                self.message_user(request,
                                  "Datoteka sesije 'session.json' nije pronađena. Pokrenite 'fetch_instagram_posts' komandu.",
                                  messages.ERROR)
                return HttpResponseRedirect(redirect_url)

            cl.load_settings(session_file)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

            # Instagrapi sada vraća media_pk kao string, Django model očekuje int.
            # cl.media_id vraća pk od URL-a, a za edit treba pk.
            media_pk = post.instagram_pk
            new_caption = post.content if post.content else ""

            cl.media_edit(media_pk, new_caption)
            post.published = True
            post.save()

            self.message_user(request, "Opis objave je uspješno ažuriran na Instagramu.", messages.SUCCESS)
        except LoginRequired:
            self.message_user(request,
                              "Instagram sesija je istekla. Pokrenite 'fetch_instagram_posts' komandu kako biste je osvježili.",
                              messages.ERROR)
        except ClientError as e:
            self.message_user(request, f"Greška prilikom komunikacije s Instagram API-jem: {e}", messages.ERROR)
        except Exception as e:
            self.message_user(request, f"Dogodila se neočekivana greška: {e}", messages.ERROR)

        return HttpResponseRedirect(redirect_url)


@admin.register(AccountInsight)
class AccountInsightAdmin(admin.ModelAdmin):
    list_display = ('fetched_at', 'profile_visits', 'reach', 'impressions', 'followers_delta_from_last_week')
    readonly_fields = [f.name for f in AccountInsight._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(HashtagInsight)
class HashtagInsightAdmin(admin.ModelAdmin):
    list_display = ('get_hashtag_name', 'get_post_info', 'get_post_date', 'count')
    search_fields = ('hashtag__name', 'post__instagram_id')
    list_filter = ('post__publish_date', 'hashtag')
    ordering = ('-post__publish_date', '-count')

    def get_hashtag_name(self, obj):
        return f"#{obj.hashtag.name}"

    get_hashtag_name.short_description = 'Hashtag'
    get_hashtag_name.admin_order_field = 'hashtag__name'

    def get_post_info(self, obj):
        post_admin_url = reverse('admin:instagram_instagrampost_change', args=[obj.post.pk])
        # Ispravljeno da str() poziva __str__ metodu posta
        return format_html('<a href="{}">{}</a>', post_admin_url, str(obj.post))

    get_post_info.short_description = 'Objava'
    # Ispravljeno polje za sortiranje
    get_post_info.admin_order_field = 'post'

    def get_post_date(self, obj):
        return obj.post.publish_date

    get_post_date.short_description = 'Datum objave'
    get_post_date.admin_order_field = 'post__publish_date'

    # Make this view read-only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Impression)
class ImpressionAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'value')
    list_filter = ('name', 'post__publish_date')
    search_fields = ('post__instagram_id', 'name')
    readonly_fields = ('post', 'name', 'value')
    ordering = ('-post__publish_date', '-value')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False