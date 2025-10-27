import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from instagram.services import get_instagram_client
from instagram.models import InstagramPost, ContentInsight, Hashtag, HashtagInsight, Impression

class Command(BaseCommand):
    help = 'Fetches insights data for recent Instagram posts from the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int,
            help='Broj najnovijih objava za koje se dohvaća statistika.',
        )
        parser.add_argument(
            '--instagram_id', type=str,
        )

    def handle(self, *args, **options):
        limit = options['limit']
        instagram_id = options['instagram_id']

        try:
            cl = get_instagram_client()
        except CommandError as e:
            raise e
        except Exception as e:
            raise CommandError(f"Greška prilikom inicijalizacije Instagram klijenta: {e}")

        posts_to_check = InstagramPost.objects.all().filter(instagram_pk__isnull=False)
        if instagram_id:
            posts_to_check = posts_to_check.filter(instagram_id=instagram_id)

        # Dohvaćamo samo objave koje imaju PK, jer je potreban za dohvaćanje statistike
        posts_to_check = posts_to_check.order_by('-publish_date')[:limit]

        # print(posts_to_check)
        # sys.exit()

        if not posts_to_check:
            self.stdout.write(self.style.WARNING("Nema objava u bazi podataka za koje bi se dohvatila statistika."))
            return

        # Process only posts that have the necessary PK for business insights
        # posts = InstagramPost.objects.filter(instagram_pk__isnull=False)
        # self.stdout.write(f"Found {posts.count()} posts with an Instagram PK to process.")

        for post in posts_to_check:

            self.stdout.write(f"--- Processing post: {post.instagram_id} ---")
            try:
                # Fetch detailed insights data which includes everything needed
                insights_data = cl.insights_media(post.instagram_pk)

                print(insights_data)


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
                self.stdout.write(f"  -> Updated main insights for post {post.instagram_id}.")





                hashtags = metrics_node.get('hashtags_impressions').get('hashtags').get('nodes')

                for hashtag in hashtags:
                    print(hashtag.get('name'))
                    value = hashtag.get('organic').get('value', 0)
                    name = hashtag.get('name')
                    obj, create = Hashtag.objects.get_or_create(name=name)


                    if (value > 0):
                        HashtagInsight.objects.update_or_create(
                            post=post,
                            hashtag = obj,
                            count = value
                        )

            except Exception as e:
                self.stdout.write(self.style.ERROR(e))




        self.stdout.write(self.style.SUCCESS("Finished fetching all content insights."))