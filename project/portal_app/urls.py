from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('mentor-dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<str:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<str:student_id>/', views.delete_student, name='delete_student'),
    path('edit-subjects/<str:student_id>/', views.edit_student_subjects, name='edit_student_subjects'),
    
    path('mentor/change-password/', views.mentor_change_password, name='mentor_change_password'),
    path('mentor-list/', views.admin_mentor_list, name='mentor_list'),
    path('change-mentor-password/<str:mentor_id>/', views.admin_change_mentor_password, name='change_mentor_password'),
    
    path('upload-student/', views.upload_student_page, name='upload_student_page'),
    path('upload-subject/', views.upload_subject_page, name='upload_subject_page'),
    path('upload-specialization/', views.upload_specialization_page, name='upload_specialization_page'),
    
    path('upload-student-excel/', views.upload_student_excel, name='upload_student_excel'),
    path('upload-subject-excel/', views.upload_subject_excel, name='upload_subject_excel'),
    path('upload-specialization-excel/', views.upload_specialization_excel, name='upload_specialization_excel'),
]
