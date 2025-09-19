from django.core.management.base import BaseCommand, CommandError
from instagrapi.exceptions import MediaNotFound
from instagram.models import InstagramPost, ContentInsight
from instagram.services import get_instagram_client
import time

class Command(BaseCommand):
    help = 'Fetches insights data for recent Instagram posts from the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int,
            help='Broj najnovijih objava za koje se dohvaća statistika.',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        try:
            cl = get_instagram_client()
        except CommandError as e:
            raise e
        except Exception as e:
            raise CommandError(f"Greška prilikom inicijalizacije Instagram klijenta: {e}")

        # Dohvaćamo samo objave koje imaju PK, jer je potreban za dohvaćanje statistike
        posts_to_check = InstagramPost.objects.filter(instagram_pk__isnull=False).order_by('-publish_date')[:limit]
        
        if not posts_to_check:
            self.stdout.write(self.style.WARNING("Nema objava u bazi podataka za koje bi se dohvatila statistika."))
            return

        self.stdout.write(self.style.SUCCESS(f"\nDohvaćanje statistike za najnovijih {len(posts_to_check)} objava..."))

        for post in posts_to_check:
            try:
                self.stdout.write(f"\n--- Obrada objave: {post.instagram_id} (PK: {post.instagram_pk}) ---")
                
                # Instagrapi metoda 'insights_media' je alias za 'media_info_a1' i vraća detaljan rječnik
                insights = cl.insights_media(post.instagram_pk)
                
                # Parsiranje nove strukture odgovora
                metrics_node = insights.get('inline_insights_node', {}).get('metrics', {})

                likes = insights.get('like_count') or 0
                comments = insights.get('comment_count') or 0
                saved = insights.get('save_count') or 0
                reach = metrics_node.get('reach_count') or 0
                impressions = metrics_node.get('impression_count') or 0
                profile_visits = metrics_node.get('owner_profile_views_count') or 0

                share_count_node = metrics_node.get('share_count', {})
                post_shares_node = share_count_node.get('post', {})
                shares = post_shares_node.get('value')

                ContentInsight.objects.create(
                    post=post,
                    likes=likes,
                    comments=comments,
                    reach=reach,
                    impressions=impressions,
                    saved=saved,
                    shares=shares,
                    profile_visits=profile_visits,
                )
                self.stdout.write(self.style.SUCCESS(f"Uspješno spremljena statistika za objavu {post.instagram_id}."))
                time.sleep(3)
            except MediaNotFound:
                self.stdout.write(self.style.ERROR(f"Objava s kodom {post.instagram_id} nije pronađena na Instagramu."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Neuspješno dohvaćanje statistike za objavu {post.instagram_id}: {e}"))
        
        self.stdout.write(self.style.SUCCESS('\nKomanda uspješno završena.'))