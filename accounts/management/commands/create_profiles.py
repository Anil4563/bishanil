from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import PatientProfile

class Command(BaseCommand):
    help = 'Create profiles for existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            try:
                profile = user.profile
                self.stdout.write(f'Profile exists for {user.username}')
            except:
                PatientProfile.objects.create(user=user)
                created_count += 1
                self.stdout.write(f'Created profile for {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} profiles'))