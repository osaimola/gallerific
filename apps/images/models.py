import boto3
import uuid as uuid_lib

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

from django_extensions.db.models import TimeStampedModel

# Create your models here.
def create_s3_client():
    boto_client = boto3.client("s3", aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_REGION_NAME)
    return boto_client

def squash_hsl(hsl_color):
    """convert hsl colors to string representation"""
    hue, saturation, lightness = hsl_color
    if lightness > 0.95: return 'white'
    if lightness < 0.06: return 'black'
    if saturation < 0.11: return 'gray'

    if hue < 0.042: return 'red' #ff0000 - #ff4000
    if hue < 0.125: return 'orange' #ff8000
    if hue < 0.167: return 'yellow' #ffff00
    if hue < 0.458: return 'green' #00ffbf
    if hue < 0.736: return 'blue' #4000ff
    if hue < 0.875: return 'purple' #ff00bf
    if hue < 0.958: return 'pink' #ff0040
    return 'red' #ff0000


class Image(TimeStampedModel):
    title = models.CharField(max_length=150, blank=True,)
    properties = models.TextField(null=True, blank=True,)
    colors = models.TextField(null=True, blank=True,)
    photo = models.ImageField()
    private = models.BooleanField(null=False, default=False,)
    owner = models.ForeignKey(
        User,
        verbose_name='owner',
        related_name='images',  # user.images
        on_delete=models.CASCADE,
        blank=True,
    )

    def __str__(self):
        return self.title

    # handle empty title case, upload image with uuid file name
    def save(self, *args, **kwargs):
        created = self.pk is None
        if created:
            if self.title == "":
                self.title = self.photo.name[:self.photo.name.rfind(".")]
            file_extension = self.photo.name[self.photo.name.rfind("."):]
            self.photo.name = f'{uuid_lib.uuid4()}{file_extension}'
        super(Image, self).save(*args, **kwargs)

    # generate presigned aws s3 url
    @property
    def get_image_url(self, expiration=30):
        client = create_s3_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        return client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': settings.AWS_STORAGE_MEDIA_FOLDER + self.photo.name,
            },
            ExpiresIn=expiration,
        )
