from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from core.models import Department


class Command(BaseCommand):
    help = 'Set up the initial audit management system with groups, departments, and sample users'

    def handle(self, *args, **options):
        self.stdout.write('Setting up Audit Management System...')
        
        # Create user groups
        self.stdout.write('Creating user groups...')
        audit_managers_group, created = Group.objects.get_or_create(name='Audit Managers')
        auditors_group, created = Group.objects.get_or_create(name='Auditors')
        department_managers_group, created = Group.objects.get_or_create(name='Department Managers')
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ User groups created'))
        else:
            self.stdout.write(self.style.WARNING('! User groups already exist'))
        
        # Create departments
        self.stdout.write('Creating departments...')
        departments_data = [
            'Finance Department',
            'Human Resources',
            'Information Technology',
            'Operations',
            'Marketing',
            'Legal Department',
            'Compliance',
            'Risk Management'
        ]
        
        for dept_name in departments_data:
            dept, created = Department.objects.get_or_create(name=dept_name)
            if created:
                self.stdout.write(f'✓ Created department: {dept_name}')
        
        # Create sample users
        self.stdout.write('Creating sample users...')
        
        # Audit Manager
        audit_manager, created = User.objects.get_or_create(
            username='audit_manager',
            defaults={
                'email': 'audit.manager@company.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'password': make_password('password123'),
                'is_staff': True
            }
        )
        if created:
            audit_manager.groups.add(audit_managers_group)
            self.stdout.write('✓ Created Audit Manager: audit_manager (password: password123)')
        else:
            self.stdout.write('! Audit Manager already exists')
        
        # Auditors
        auditors_data = [
            {'username': 'auditor1', 'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice.smith@company.com'},
            {'username': 'auditor2', 'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob.johnson@company.com'},
            {'username': 'auditor3', 'first_name': 'Carol', 'last_name': 'Williams', 'email': 'carol.williams@company.com'},
        ]
        
        for auditor_data in auditors_data:
            auditor, created = User.objects.get_or_create(
                username=auditor_data['username'],
                defaults={
                    'email': auditor_data['email'],
                    'first_name': auditor_data['first_name'],
                    'last_name': auditor_data['last_name'],
                    'password': make_password('password123'),
                }
            )
            if created:
                auditor.groups.add(auditors_group)
                self.stdout.write(f'✓ Created Auditor: {auditor_data["username"]} (password: password123)')
            else:
                self.stdout.write(f'! Auditor {auditor_data["username"]} already exists')
        
        # Department Managers
        dept_managers_data = [
            {'username': 'finance_manager', 'first_name': 'David', 'last_name': 'Brown', 'email': 'david.brown@company.com', 'dept': 'Finance Department'},
            {'username': 'hr_manager', 'first_name': 'Emma', 'last_name': 'Davis', 'email': 'emma.davis@company.com', 'dept': 'Human Resources'},
            {'username': 'it_manager', 'first_name': 'Frank', 'last_name': 'Miller', 'email': 'frank.miller@company.com', 'dept': 'Information Technology'},
        ]
        
        for manager_data in dept_managers_data:
            manager, created = User.objects.get_or_create(
                username=manager_data['username'],
                defaults={
                    'email': manager_data['email'],
                    'first_name': manager_data['first_name'],
                    'last_name': manager_data['last_name'],
                    'password': make_password('password123'),
                }
            )
            if created:
                manager.groups.add(department_managers_group)
                # Assign to department
                try:
                    dept = Department.objects.get(name=manager_data['dept'])
                    dept.manager = manager
                    dept.save()
                except Department.DoesNotExist:
                    self.stdout.write(f'! Department {manager_data["dept"]} not found')
                
                self.stdout.write(f'✓ Created Department Manager: {manager_data["username"]} (password: password123)')
            else:
                self.stdout.write(f'! Department Manager {manager_data["username"]} already exists')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@company.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created superuser: admin (password: admin123)'))
        else:
            self.stdout.write('! Superuser already exists')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Audit Management System setup completed!'))
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('  • Admin: admin / admin123')
        self.stdout.write('  • Audit Manager: audit_manager / password123')
        self.stdout.write('  • Auditors: auditor1, auditor2, auditor3 / password123')
        self.stdout.write('  • Department Managers: finance_manager, hr_manager, it_manager / password123')
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Run migrations: python manage.py migrate')
        self.stdout.write('  2. Start the server: python manage.py runserver')
        self.stdout.write('  3. Login and start creating audit projects!')
