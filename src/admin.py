from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, User, Imagen, Tarea, Tag, TareaHasTag


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission', 'created_at')
    search_fields = ('role', 'permission')
    ordering = ('id',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'name', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('name',)
    ordering = ('-created_at',)

    # Adaptación de fieldsets porque usamos 'name' en vez de 'username'
    fieldsets = (
        (None, {'fields': ('name', 'password')}),
        ('Rol', {'fields': ('role',)}),
        ('Permisos Django', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagen', 'thumbnail', 'created_at')
    readonly_fields = ('thumbnail', 'created_at', 'updated_at')


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'user', 'estado', 'prioridad', 'imagen', 'created_at')
    list_filter = ('estado', 'prioridad', 'user')
    search_fields = ('titulo', 'descripcion')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'created_at')
    search_fields = ('tag',)


@admin.register(TareaHasTag)
class TareaHasTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tarea', 'tag', 'created_at')
    list_filter = ('tag',)
