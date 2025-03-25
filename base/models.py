from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils.timezone import now

class CustomUserManager(UserManager):
    def _create_user(self, email: str, username: str, password: str, **extra_fields) -> 'User':
        """
        Create and save a User with the given email, username, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, username=None, password=None, **extra_fields) -> 'User':
        """
        Create and save a regular User with the given email, username, and password.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email=None, username=None, password=None, **extra_fields) -> 'User':
        """
        Create and save a SuperUser with the given email, username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True)
    first_name = models.CharField(max_length=200, blank=False)
    last_name = models.CharField(max_length=200, blank=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # User Permissions/misc
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    creation_date = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'

    def get_full_name(self) -> str:
        """
        Return the user's full name.
        """
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self) -> str:
        """
        Return the user's short name.
        """
        return self.email.split('@')[0]

    def __str__(self) -> str:
        """
        Return a string representation of the user.
        """
        return f'{self.email} - ({self.user_id})'
    
class IFTAR(models.Model):
    id = models.AutoField(primary_key=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=500)
    time = models.DateTimeField(default=timezone.now)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)

    class Meta:
        verbose_name = 'IFTAR'
        verbose_name_plural = 'IFTARs'
        db_table = 'iftar'
        ordering = ['-time']
    
    def __str__(self) -> str:
        return f'{self.title} - ({self.id})'
    
    def get_participants(self) -> str:
        return ', '.join([participant.get_full_name() for participant in self.participants.all()])
    
    def get_host(self) -> str:
        return self.host.get_full_name()
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)
    host = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username} - {self.message[:20]}'
    
from django.db.models.signals import m2m_changed

@receiver(m2m_changed, sender=IFTAR.participants.through)
def notify_participants_m2m(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        participants = instance.participants.filter(pk__in=pk_set)
        for participant in participants:
            Notification.objects.create(
                user=participant,
                message=f"You have been invited to '{instance.title}' at {instance.location} on {instance.time}.",
                host=instance.host,
                is_read=False
            )

