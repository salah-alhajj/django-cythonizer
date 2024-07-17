import os
import django
import random
from datetime import timedelta
from django.utils import timezone
import uuid

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Root.settings")
django.setup()

from django.contrib.auth.models import User
from employees.models import *
from finance.models import *
from notifications.models import *
from projects.models import *
from reporting.models import *
from time_tracking.models import *
from faker import Faker

fake = Faker()

# Lists for departments, jobs, and skills (as before)
DEPARTMENTS = [
    ("Human Resources", "Manages employee relations, recruitment, and company policies."),
    ("Finance", "Handles company finances, budgeting, and financial reporting."),
    ("Marketing", "Develops and implements marketing strategies to promote the company."),
    ("Sales", "Responsible for selling company products or services to customers."),
    ("IT", "Manages company technology infrastructure and software development."),
    ("Operations", "Oversees day-to-day operations and ensures efficiency."),
    ("Research and Development", "Focuses on innovation and developing new products or services."),
    ("Customer Service", "Handles customer inquiries, complaints, and support."),
    ("Legal", "Manages legal affairs and ensures company compliance."),
    ("Product Management", "Oversees product development and lifecycle."),
]

JOBS = [
    ("Software Engineer", 60000, 150000),
    ("Marketing Specialist", 45000, 90000),
    ("Sales Representative", 40000, 100000),
    ("Human Resources Manager", 60000, 120000),
    ("Financial Analyst", 55000, 110000),
    ("Project Manager", 70000, 140000),
    ("Customer Service Representative", 35000, 60000),
    ("Data Scientist", 80000, 160000),
    ("Product Manager", 75000, 150000),
    ("Operations Coordinator", 45000, 80000),
    ("Legal Counsel", 90000, 180000),
    ("UX Designer", 60000, 120000),
    ("Business Analyst", 55000, 110000),
    ("Quality Assurance Tester", 50000, 100000),
    ("Network Administrator", 60000, 120000),
]

SKILLS = [
    "Python Programming", "Java Programming", "JavaScript", "SQL", "Data Analysis",
    "Project Management", "Digital Marketing", "Sales Techniques", "Customer Service",
    "Financial Modeling", "Legal Research", "UX/UI Design", "Agile Methodologies",
    "Network Security", "Cloud Computing", "Machine Learning", "SEO Optimization",
    "Content Writing", "Public Speaking", "Leadership", "Problem Solving",
    "Time Management", "Teamwork", "Communication", "Negotiation",
    "Microsoft Office Suite", "Adobe Creative Suite", "Salesforce CRM",
    "Business Strategy", "Market Research", "Product Development",
    "Quality Assurance", "Risk Management", "Supply Chain Management",
    "Database Administration", "Mobile App Development", "Web Development",
    "Social Media Management", "Data Visualization", "Statistical Analysis",
    "Cybersecurity", "DevOps", "Blockchain", "Artificial Intelligence",
    "Virtual Reality", "Augmented Reality", "IoT Development", "Robotics",
    "3D Modeling", "Video Editing", "Graphic Design", "Technical Writing"
]

def create_realistic_mockup_data():
    # Check for existing data
    departments = Department.objects.all()
    skills = Skill.objects.all()
    employees = list(Employee.objects.all())

    if not departments.exists() or not skills.exists() or not employees:
        print("Error: Departments, Skills, or Employees are missing. Please ensure they are created before running this script.")
        return

    print(f"Found {departments.count()} departments, {skills.count()} skills, and {len(employees)} employees.")

    # Create Departments
    departments = [Department.objects.create(
        name=name,
        description=description,
        budget=random.uniform(500000, 5000000)
    ) for name, description in DEPARTMENTS]

    # Create Skills
    skills = [Skill.objects.create(
        name=skill_name,
        description=f"Proficiency in {skill_name}"
    ) for skill_name in SKILLS]

    # Create Employees and related data
    for i in range(10000):
        job_title, min_salary, max_salary = random.choice(JOBS)
        hire_date = fake.date_between(start_date='-20y', end_date='today')
        
        username = f"{fake.user_name()}_{uuid.uuid4().hex[:8]}"
        
        user = User.objects.create_user(
            username=username,
            email=fake.email(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )

        employee = Employee.objects.create(
            user=user,
            department=random.choice(departments),
            position=job_title,
            salary=random.uniform(min_salary, max_salary),
            hire_date=hire_date,
            performance_score=min(random.uniform(5, 10), 10)
        )

        employees.append(employee)

        # Add skills to employee
        employee_skills = random.sample(skills, random.randint(3, 8))
        for skill in employee_skills:
            EmployeeSkill.objects.create(
                employee=employee,
                skill=skill,
                proficiency_level=random.randint(1, 5)
            )

        if i % 100 == 0:
            print(f"Created {i} employees...")

    print(f"Found {len(employees)} employees.")
    # Create Performance Reviews
    for employee in employees:
        num_reviews = min(int((timezone.now().date() - employee.hire_date).days / 365), 5)
        for _ in range(num_reviews):
            review_date = fake.date_between(start_date=employee.hire_date, end_date='today')
            reviewer = random.choice([e for e in employees if e != employee])
            PerformanceReview.objects.create(
                employee=employee,
                reviewer=reviewer,
                review_date=review_date,
                score=min(random.uniform(employee.performance_score - 1, employee.performance_score + 1), 10),
                comments=fake.paragraph(nb_sentences=3),
                goals=fake.paragraph(nb_sentences=2)
            )

    print("Employee data creation completed!")
    

    # Create Projects
    projects = []
    for i in range(500):
        project = Project.objects.create(
            name=fake.catch_phrase(),
            description=fake.text(),
            start_date=fake.date_this_year(),
            end_date=fake.date_this_year(after_today=True),
            budget=random.uniform(10000, 1000000),
            manager=random.choice(employees),
            department=random.choice(departments),
            status=random.choice(['planning', 'in_progress', 'completed', 'on_hold'])
        )
        projects.append(project)
        team_size = min(random.randint(3, 15), len(employees))
        project.team_members.set(random.sample(employees, team_size))
        if i % 50 == 0:
            print(f"Created {i} projects...")

    print("Project data creation completed!")

    # Create Tasks
    print(f"Found {len(projects)} existing projects.")

    for i, project in enumerate(projects):
        team_members = list(project.team_members.all())
        if not team_members:
            print(f"Warning: Project {project.id} has no team members. Skipping task creation for this project.")
            continue

        num_tasks = random.randint(5, 20)
        for _ in range(num_tasks):
            try:
                task_due_date = fake.date_between(start_date=project.start_date, end_date=project.end_date)
            except ValueError:
                task_due_date = project.end_date

            Task.objects.create(
                title=fake.sentence(),
                description=fake.paragraph(),
                project=project,
                assigned_to=random.choice(team_members),
                due_date=task_due_date,
                priority=random.randint(1, 5),
                status=random.choice(['not_started', 'in_progress', 'completed', 'blocked']),
                estimated_hours=random.uniform(1, 40)
            )
        if i % 50 == 0:
            print(f"Created tasks for {i} projects...")

    print("Task data creation completed!")

    

    
    # Create Expenses
    for i in range(5000):
        Expense.objects.create(
            project=random.choice(projects),
            employee=random.choice(employees),
            amount=random.uniform(10, 1000),
            date=fake.date_this_year(),
            description=fake.sentence(),
            status=random.choice(['submitted', 'approved', 'rejected', 'reimbursed'])
        )
        if i % 500 == 0:
            print(f"Created {i} expenses...")

    print("Expense data creation completed!")

    # Create Reports
    for i, project in enumerate(projects):
        if not project.team_members.all():
            print(f"Warning: Project {project.id} has no team members. Skipping task creation for this project.")
            continue
        num_reports = random.randint(1, 5)
        for _ in range(num_reports):
             
            Report.objects.create(
                title=fake.catch_phrase(),
                project=project,
                author=random.choice(list(project.team_members.all())),
                content='\n'.join(fake.paragraphs(nb=3)),
                created_at=fake.date_time_this_year(),
                approved_by=project.manager
            )
        if i % 50 == 0:
            print(f"Created reports for {i} projects...")

    print("Report data creation completed!")

    # Create Notifications

    for i, employee in enumerate(employees):
        num_notifications = random.randint(0, 10)
        for _ in range(num_notifications):
            Notification.objects.create(
                recipient=employee,
                message=fake.sentence(),
                created_at=fake.date_time_this_month(),
                read=random.choice([True, False]),
                related_task=random.choice(Task.objects.all()) if random.choice([True, False]) else None,
                related_project=random.choice(projects) if random.choice([True, False]) else None
            )
        if i % 10 == 0:
            print(f"Created notifications for {i} employees...")

    print("Notification data creation completed!")

    print("All realistic mockup data creation completed successfully!")

if __name__ == "__main__":
    create_realistic_mockup_data()