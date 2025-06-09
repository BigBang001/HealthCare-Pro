from django.contrib import admin
from .models import Patient, Doctor, PatientDoctorMapping

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'gender', 'created_by_user', 'created_at')
    search_fields = ('name', 'gender')
    list_filter = ('gender',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'experience_years', 'created_at')
    search_fields = ('name', 'specialization')
    list_filter = ('specialization',)

@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'assigned_by_user', 'created_at')
    search_fields = ('patient__name', 'doctor__name')
    list_filter = ('doctor',)
