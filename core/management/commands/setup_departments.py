from django.core.management.base import BaseCommand
from core.models import Department


class Command(BaseCommand):
    help = 'Set up test departments for the audit system'

    def handle(self, *args, **options):
        departments = [
            'IT Department',
            'Finance Department',
            'Human Resources',
            'Operations',
            'Marketing',
            'Sales',
            'Customer Service',
            'Legal Department'
        ]

        for dept_name in departments:
            dept, created = Department.objects.get_or_create(name=dept_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created department: {dept_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Department already exists: {dept_name}'))

        self.stdout.write(self.style.SUCCESS('Departments setup completed!'))
