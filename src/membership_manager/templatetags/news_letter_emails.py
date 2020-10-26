from django import template

from membership_manager.utils import check_newsletter_update

register = template.Library()

@register.simple_tag()
def update_emails(news_letter):
    return check_newsletter_update(news_letter)