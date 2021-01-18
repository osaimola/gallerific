import boto3
from colorthief import ColorThief
import colour

from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Image


def create_s3_client():
    boto_client = boto3.client("s3", aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_REGION_NAME)
    return boto_client


def create_rekognition_client():
    boto_client = boto3.client("rekognition", aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_REGION_NAME)
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


@receiver(post_save, sender=Image)
def label_image(sender, instance, created, **kwargs):
    if created:
        # add color labels
        try:
            color_thief_object = ColorThief(instance.photo.file)
            palette = []
            for color_object in color_thief_object.get_palette(color_count=4):
                # convert color from rgb to hex to hsl for easier processing
                hsl_color = colour.hex2hsl(f'#{"{:02x}".format(color_object[0])}{"{:02x}".format(color_object[1])}{"{:02x}".format(color_object[2])}')
                palette.append(squash_hsl(hsl_color))
            instance.colors = ', '.join(palette)
        except Exception as e:
            print(e)

        # add image labels
        client = create_rekognition_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        key = settings.AWS_STORAGE_MEDIA_FOLDER + instance.photo.name
        try:
            response = client.detect_labels(Image={
                'S3Object':{
                    'Bucket':bucket,
                    'Name':key,
                }
            }, MaxLabels=5)
            labels = []
            for label in response['Labels']:
                labels.append(label['Name'])
            instance.properties = ', '.join(labels)
        except Exception as e:
            print(e)

        instance.save()


@receiver(pre_delete, sender=Image)
def delete_hosted_image(sender, instance, **Kwargs):
    client = create_s3_client()
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    key = settings.AWS_STORAGE_MEDIA_FOLDER + instance.photo.name
    try:
        client.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(e)
