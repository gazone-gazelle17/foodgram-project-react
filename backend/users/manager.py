from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(
            self,
            username,
            password,
            email,
            first_name,
            last_name
    ):
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
            self,
            username,
            password,
            email,
            first_name='',
            last_name=''
    ):
        user = self.create_user(
            username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
