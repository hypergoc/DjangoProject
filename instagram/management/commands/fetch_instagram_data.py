from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from urllib import request as url_request
from instagram.services import get_instagram_client
from instagram.models import InstagramPost, ContentInsight, AccountInsight

class Command(BaseCommand):
    help = 'Prijavljuje se na Instagram, osvježava sesiju i dohvaća najnovije objave i statistike.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='Broj najnovijih objava za dohvaćanje.',
        )

    def handle(self, *args, **options):
        self.stdout.write("Pokretanje procesa dohvaćanja podataka s Instagrama...")
        
        try:
            cl = get_instagram_client()
        except CommandError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return

        user_id = cl.user_id_from_username(cl.username)
        num_posts_to_fetch = options['posts']
        
        self.stdout.write(f"Dohvaćanje zadnjih {num_posts_to_fetch} objava za korisnika {cl.username}...")
        
        medias = cl.user_medias(user_id, num_posts_to_fetch)
        
        if not medias:
            self.stdout.write(self.style.WARNING("Nema pronađenih objava."))
            # Ipak, pokušaj dohvatiti statistiku računa
        else:
            for media in medias:
                self.stdout.write(f"  - Procesiram objavu {media.code}...")
                
                post, created = InstagramPost.objects.update_or_create(
                    instagram_id=media.code,
                    defaults={
                        'instagram_pk': str(media.pk),
                        'content': media.caption_text,
                        'post_url': f"https://www.instagram.com/p/{media.code}/",
                        'publish_date': media.taken_at,
                        'post_song': f"{media.music_info.title} by {media.music_info.artist}" if hasattr(media, 'music_info') and media.music_info else None,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"    -> Kreirana nova objava u bazi."))
                    if media.thumbnail_url:
                        try:
                            response = url_request.urlopen(str(media.thumbnail_url))
                            post.post_image.save(f"{media.code}.jpg", ContentFile(response.read()), save=True)
                            self.stdout.write(f"    -> Slika preuzeta i spremljena.")
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"    -> Greška pri preuzimanju slike: {e}"))
                else:
                    self.stdout.write(f"    -> Objava ažurirana u bazi.")

                try:
                    insight_data = cl.media_info(media.pk).dict()
                    if insight_data.get('like_count') is not None:
                        ContentInsight.objects.create(
                            post=post,
                            likes=insight_data.get('like_count', 0),
                            comments=insight_data.get('comment_count', 0),
                            reach=insight_data.get('reach_count', 0),
                            impressions=insight_data.get('impression_count', 0),
                            saved=insight_data.get('saved_count', 0),
                        )
                        self.stdout.write(f"    -> Statistika objave spremljena.")
                    else:
                         self.stdout.write(self.style.WARNING(f"    -> Statistika za ovu objavu nije dostupna."))
                except Exception:
                    self.stdout.write(self.style.WARNING(f"    -> Nije moguće dohvatiti statistiku za objavu {media.code}."))
        
        self.stdout.write("\nDohvaćanje statistike računa...")
        try:
            insights = cl.business_account_insights(last_days=7)
            if insights:
                AccountInsight.objects.create(
                    profile_visits=insights.get('profile_views', {}).get('value', 0),
                    followers_delta_from_last_week=insights.get('follower_count', {}).get('value', 0),
                    gender_graph=insights.get('audience_gender_age', {}),
                    followers_top_cities_graph=insights.get('audience_city', {}),
                    followers_top_countries_graph=insights.get('audience_country', {}),
                    impressions=insights.get('impressions', {}).get('value', 0),
                    reach=insights.get('reach', {}).get('value', 0),
                )
                self.stdout.write(self.style.SUCCESS("Statistika računa uspješno spremljena."))
            else:
                 self.stdout.write(self.style.WARNING("Nije moguće dohvatiti statistiku računa."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Greška pri dohvaćanju statistike računa: {e}. Provjerite imate li Business/Creator račun."))

        self.stdout.write(self.style.SUCCESS("\nProces završen."))