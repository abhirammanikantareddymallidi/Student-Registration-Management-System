from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    
    # Mentor Fields
    mentor_name = models.CharField(max_length=100, null=True, blank=True)
    mentor_id = models.CharField(max_length=50, null=True, blank=True)
    mentor_phone = models.CharField(max_length=50, null=True, blank=True)
    mentor_email = models.EmailField(null=True, blank=True)
    # Keeping mentor_password for the portal functionality
    mentor_password = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} ({self.student_id})"

    @property
    def total_subjects_count(self):
        return self.subjects.count()

    @property
    def completed_subjects_count(self):
        return self.subjects.filter(course_completed=True).count()

class SubjectMaster(models.Model):
    subject_id = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    specialization = models.CharField(max_length=50)
    cluster1_start = models.IntegerField(default=0)
    cluster1_end = models.IntegerField(default=0)
    cluster2_start = models.IntegerField(default=0)
    cluster2_end = models.IntegerField(default=0)

    class Meta:
        unique_together = ('subject_id', 'department', 'specialization')

    def __str__(self):
        return f"{self.subject_name} ({self.subject_id}) - {self.specialization}"

class SpecializationMapping(models.Model):
    # ... (remains same)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    bucket = models.CharField(max_length=20)  # C0, C1, etc.
    subject_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.specialization} - {self.bucket}: {self.subject_id}"

class Subject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subjects')
    subject_id = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)
    course_completed = models.BooleanField(default=False)
    bucket = models.CharField(max_length=20, null=True, blank=True)
    cluster1_start = models.IntegerField(null=True, blank=True)
    cluster1_end = models.IntegerField(null=True, blank=True)
    cluster2_start = models.IntegerField(null=True, blank=True)
    cluster2_end = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject_name} ({self.subject_id}) for {self.student.student_name}"

    @property
    def get_display_name(self):
        return self.subject_name
