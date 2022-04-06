import init_project
from main.models import Region
from slugify import slugify

def main():
    for r in Region.objects.all():
        r.slug = slugify(r.name)
        r.save()


if __name__ == "__main__":
    main()
