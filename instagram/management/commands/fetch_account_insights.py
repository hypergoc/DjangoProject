from django.core.management.base import BaseCommand, CommandError
from instagram.models import AccountInsight
from instagram.services import get_instagram_client

class Command(BaseCommand):
    help = 'Fetches insights data for the Instagram account and saves it to the database.'

    def handle(self, *args, **options):
        try:
            cl = get_instagram_client()
        except CommandError as e:
            raise e
        except Exception as e:
            raise CommandError(f"Greška prilikom inicijalizacije Instagram klijenta: {e}")

        self.stdout.write("Dohvaćanje statistike računa...")
        try:
            insights = cl.insights_account()
            
            account_unit = insights.get('account_insights_unit', {})
            followers_unit = insights.get('followers_unit', {})
            
            AccountInsight.objects.create(
                profile_visits=account_unit.get('profile_visits_metric_count') or 0,
                followers_delta_from_last_week=followers_unit.get('followers_delta_from_last_week') or 0,
                gender_graph=followers_unit.get('gender_graph', {}),
                all_followers_age_graph=followers_unit.get('all_followers_age_graph', {}),
                followers_top_cities_graph=followers_unit.get('followers_top_cities_graph', {}),
                followers_top_countries_graph=followers_unit.get('followers_top_countries_graph', {}),
                week_daily_followers_graph=followers_unit.get('week_daily_followers_graph', {}),
                impressions=account_unit.get('impressions_metric_count'),
                reach=account_unit.get('reach_metric_count'),
            )
            self.stdout.write(self.style.SUCCESS('Uspješno dohvaćena i spremljena statistika računa.'))

        except Exception as e:
            raise CommandError(f"Neuspješno dohvaćanje ili spremanje statistike računa: {e}")