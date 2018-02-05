from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models.userProfile import UserProfileModel

from .models.worker import WorkerModel, PoolModel, WorkerStats


class ProfileModelInline(admin.StackedInline):
    model = UserProfileModel
    can_delete = False
    verbose_name_plural = 'PROFILE INFO'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileModelInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
admin.site.register(WorkerModel)
admin.site.register(PoolModel)
admin.site.register(WorkerStats)