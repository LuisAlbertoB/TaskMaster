import os
from io import BytesIO
from PIL import Image as PilImage
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from src.models import Role, User, Imagen, Tarea, Tag, TareaHasTag


def create_dummy_image_file(name='test.jpg', size=(100, 100), fmt='JPEG'):
    """Helper para crear una imagen en memoria."""
    file = BytesIO()
    image = PilImage.new('RGB', size, color='blue')
    image.save(file, fmt)
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type=f'image/{fmt.lower()}')


class TaskMasterVerificationTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Roles
        self.root_role = Role.objects.create(role='superuser', permission='root')
        self.user_role = Role.objects.create(role='user', permission='user')

        # Usuarios
        self.user_a = User.objects.create_user(
            name='user_a',
            password='Password123!',
            role=self.user_role
        )
        self.user_b = User.objects.create_user(
            name='user_b',
            password='Password123!',
            role=self.user_role
        )
        self.root_user = User.objects.create_superuser(
            name='superuser',
            password=None,  # Superuser inicial sin contraseña
            role=self.root_role
        )

        # Tags
        self.tag_1 = Tag.objects.create(tag='Programacion')
        self.tag_2 = Tag.objects.create(tag='Diseño')

    # ─── 1. VERIFICACIÓN DE BCRYPT ───────────────────────────────────────────
    def test_bcrypt_password_hashing(self):
        """Verifica que el hasher primario sea BCryptSHA256PasswordHasher y genere hashes bcrypt."""
        self.assertIn(
            'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
            settings.PASSWORD_HASHERS[0]
        )
        # La contraseña de user_a fue encriptada con Bcrypt
        self.assertTrue(self.user_a.password.startswith('bcrypt_sha256$'))

    # ─── 2. VERIFICACIÓN DE CONFIGURACIÓN MEDIA ──────────────────────────────
    def test_media_configuration_and_absolute_urls(self):
        """Verifica la configuración de MEDIA_URL, MEDIA_ROOT y generación de URLs absolutas."""
        self.assertEqual(settings.MEDIA_URL, '/media/')
        self.assertTrue(str(settings.MEDIA_ROOT).endswith('media'))

        self.client.force_authenticate(user=self.user_a)
        img_file = create_dummy_image_file()

        url = reverse('imagen-list')
        response = self.client.post(url, {'imagen': img_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['imagen_url'].startswith('http://testserver/media/'))
        self.assertTrue(response.data['thumbnail_url'].startswith('http://testserver/media/'))

    # ─── 3. VERIFICACIÓN DE MINIATURAS PILLOW (THUMBNAIL GENERATION) ─────────
    def test_pillow_thumbnail_generation(self):
        """Verifica que Pillow genera automáticamente la miniatura al subir una imagen."""
        img_file = create_dummy_image_file(name='original.jpg', size=(800, 600))
        imagen = Imagen.objects.create(imagen=img_file)

        self.assertIsNotNone(imagen.thumbnail)
        self.assertTrue(os.path.exists(imagen.thumbnail.path))

        # Verificar dimensiones del thumbnail (<= 300x300)
        with PilImage.open(imagen.thumbnail.path) as thumb_img:
            w, h = thumb_img.size
            self.assertLessEqual(w, 300)
            self.assertLessEqual(h, 300)

    # ─── 4. VERIFICACIÓN DE LIMPIEZA DE ARCHIVOS HUÉRFANOS ───────────────────
    def test_deleting_tarea_cleans_up_media_files(self):
        """Al eliminar una tarea, se elimina su Imagen asociada y los archivos del disco."""
        img_file = create_dummy_image_file()
        imagen = Imagen.objects.create(imagen=img_file)
        img_path = imagen.imagen.path
        thumb_path = imagen.thumbnail.path if imagen.thumbnail else None

        tarea = Tarea.objects.create(user=self.user_a, titulo="Tarea de Prueba", imagen=imagen)
        self.assertTrue(os.path.exists(img_path))

        # Eliminar la tarea
        self.client.force_authenticate(user=self.user_a)
        url = reverse('tarea-detail', kwargs={'pk': tarea.id})
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Los archivos físicos en disco y la entrada de BD deben haber sido borrados
        self.assertFalse(Imagen.objects.filter(id=imagen.id).exists())
        self.assertFalse(os.path.exists(img_path))
        if thumb_path:
            self.assertFalse(os.path.exists(thumb_path))

    # ─── 5. VERIFICACIÓN DE PROTECCIÓN DE RUTAS (OBJECT-LEVEL PERMISSIONS) ───
    def test_object_level_permissions_privacy_and_403_forbidden(self):
        """
        - Privacidad: User A solo ve sus tareas en la lista.
        - Restricción: User B intentando editar o borrar tarea de User A recibe 403 Forbidden.
        """
        tarea_a = Tarea.objects.create(user=self.user_a, titulo="Tarea de User A")
        tarea_b = Tarea.objects.create(user=self.user_b, titulo="Tarea de User B")

        # 1. Privacidad en Listado
        self.client.force_authenticate(user=self.user_a)
        url_list = reverse('tarea-list')
        res_list = self.client.get(url_list)
        results = res_list.data.get('results', res_list.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], tarea_a.id)

        # 2. Intento de User B de editar tarea de User A -> 403 Forbidden
        self.client.force_authenticate(user=self.user_b)
        url_detail = reverse('tarea-detail', kwargs={'pk': tarea_a.id})
        res_put = self.client.put(url_detail, {'titulo': 'Hack'}, format='json')
        self.assertEqual(res_put.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Intento de User B de borrar tarea de User A -> 403 Forbidden
        res_del = self.client.delete(url_detail)
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)

    # ─── 6. VERIFICACIÓN DE CRUD COMPLETO (TAREAS, USUARIOS, TAGS) ────────────
    def test_crud_tags(self):
        """CRUD para la entidad Tags."""
        self.client.force_authenticate(user=self.user_a)
        # Create
        url = reverse('tag-list')
        res_create = self.client.post(url, {'tag': 'Verificacion'}, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        tag_id = res_create.data['id']

        # Read
        res_get = self.client.get(reverse('tag-detail', kwargs={'pk': tag_id}))
        self.assertEqual(res_get.data['tag'], 'Verificacion')

        # Update
        res_put = self.client.put(reverse('tag-detail', kwargs={'pk': tag_id}), {'tag': 'Verificacion_Editada'}, format='json')
        self.assertEqual(res_put.status_code, status.HTTP_200_OK)

        # Delete
        res_del = self.client.delete(reverse('tag-detail', kwargs={'pk': tag_id}))
        self.assertEqual(res_del.status_code, status.HTTP_204_NO_CONTENT)

    def test_crud_users_and_put_password(self):
        """CRUD para la entidad Usuarios, incluyendo establecer contraseña vía PUT."""
        self.client.force_authenticate(user=self.root_user)

        # 1. Establecer contraseña del superuser creado en el seed vía PUT
        url_superuser = reverse('user-detail', kwargs={'pk': self.root_user.id})
        res_put_pass = self.client.put(url_superuser, {'name': 'superuser', 'password': 'NewSuperuserPass123!'}, format='json')
        self.assertEqual(res_put_pass.status_code, status.HTTP_200_OK)

        self.root_user.refresh_from_db()
        self.assertTrue(self.root_user.check_password('NewSuperuserPass123!'))

        # 2. Crear nuevo usuario
        res_create = self.client.post(reverse('user-list'), {'name': 'user_crud', 'password': 'UserPass123!'}, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        new_user_id = res_create.data['id']

        # 3. Eliminar usuario
        res_del = self.client.delete(reverse('user-detail', kwargs={'pk': new_user_id}))
        self.assertEqual(res_del.status_code, status.HTTP_204_NO_CONTENT)
