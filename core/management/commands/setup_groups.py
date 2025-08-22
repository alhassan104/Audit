from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Set up user groups and create test users for the audit system'

    def handle(self, *args, **options):
        # Create groups
        audit_managers_group, created = Group.objects.get_or_create(name="Audit Managers")
        if created:
            self.stdout.write(self.style.SUCCESS('Created Audit Managers group'))
        else:
            self.stdout.write(self.style.WARNING('Audit Managers group already exists'))

        auditors_group, created = Group.objects.get_or_create(name="Auditors")
        if created:
            self.stdout.write(self.style.SUCCESS('Created Auditors group'))
        else:
            self.stdout.write(self.style.WARNING('Auditors group already exists'))

        # Create test audit manager user
        if not User.objects.filter(username='manager').exists():
            manager_user = User.objects.create(
                username='manager',
                email='manager@example.com',
                password=make_password('manager123'),
                first_name='Test',
                last_name='Manager'
            )
            manager_user.groups.add(audit_managers_group)
            self.stdout.write(self.style.SUCCESS('Created test manager user (username: manager, password: manager123)'))
        else:
            self.stdout.write(self.style.WARNING('Test manager user already exists'))

        # Create test auditor user
        if not User.objects.filter(username='auditor').exists():
            auditor_user = User.objects.create(
                username='auditor',
                email='auditor@example.com',
                password=make_password('auditor123'),
                first_name='Test',
                last_name='Auditor'
            )
            auditor_user.groups.add(auditors_group)
            self.stdout.write(self.style.SUCCESS('Created test auditor user (username: auditor, password: auditor123)'))
        else:
            self.stdout.write(self.style.WARNING('Test auditor user already exists'))

        self.stdout.write(self.style.SUCCESS('Setup completed successfully!'))
