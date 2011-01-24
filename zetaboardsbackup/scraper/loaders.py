import datetime
import re
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import Join, TakeFirst, MapCompose

from forum.models import UserGroup

def extract_numbers(s):
    regex = re.compile("(?P<id>[0-9]+)")
    r = regex.search(s)
    if r:
        return r.groups()[0]
    else:
        return None

def get_or_create_user_group_from_title(s):
    user_group, created = UserGroup.objects.get_or_create(title=s)
    return user_group

def strip_start_date(s):
    return s.replace('Start Date ', '')

def to_datetime_long(s):
    dt = datetime.datetime.strptime(s, '%b %d %Y, %I:%M %p')
    return dt

def to_datetime_short(s):
    dt = datetime.datetime.strptime(s, '%B %d, %Y')
    print dt
    return dt

def to_int(s):
    non_decimal = re.compile(r'[^\d]+')
    return non_decimal.sub('', s)


class ForumLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)


class ThreadLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)
    user_in = MapCompose(unicode.strip)
    replies_in = MapCompose(unicode.strip, to_int)
    views_in = MapCompose(unicode.strip, to_int)
    date_posted_in = MapCompose(unicode.strip, strip_start_date, to_datetime_long)


class PostLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)


class RawPostLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)


class UserLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)
    user_group_in = MapCompose(unicode.strip, get_or_create_user_group_from_title)
    member_number_in = MapCompose(unicode.strip, extract_numbers)
    post_count_in = MapCompose(unicode.strip, to_int)
    signature_in = Join()
    date_birthday_in = MapCompose(unicode.strip, to_datetime_short)
    date_joined_in = MapCompose(unicode.strip, to_datetime_short)


class UserGroupLoader(XPathItemLoader):
    default_output_processor = TakeFirst()
