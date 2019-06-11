"""
This module contains various configuration settings via
waffle switches for the contentstore app.
"""
from openedx.core.djangoapps.waffle_utils import CourseWaffleFlag, WaffleFlagNamespace, WaffleSwitchNamespace

# Namespace
WAFFLE_NAMESPACE = u'studio'

# Switches
ENABLE_ACCESSIBILITY_POLICY_PAGE = u'enable_policy_page'

# Global dictionary to store proctoring provider specific waffle flags
REVIEW_RULES_PER_PROCTORING_PROVIDER = {}

def create_review_rules_for_provider_waffle_flag(provider_name):
    """
    Creates a waffle flag with the following name format: studio.show_review_rules_for_<provider_name>
    and returns it to the user
    """
    flag_name = u'show_review_rules_for_{}'.format(provider_name)
    new_flag = CourseWaffleFlag(
        waffle_namespace=waffle_flags(),
        flag_name=flag_name,
        flag_undefined_default=False
    )
    return new_flag

def waffle():
    """
    Returns the namespaced, cached, audited Waffle Switch class for Studio pages.
    """
    return WaffleSwitchNamespace(name=WAFFLE_NAMESPACE, log_prefix=u'Studio: ')


def waffle_flags():
    """
    Returns the namespaced, cached, audited Waffle Flag class for Studio pages.
    """
    return WaffleFlagNamespace(name=WAFFLE_NAMESPACE, log_prefix=u'Studio: ')

# Flags
ENABLE_PROCTORING_PROVIDER_OVERRIDES = CourseWaffleFlag(
    waffle_namespace=waffle_flags(),
    flag_name=u'enable_proctoring_provider_overrides',
    flag_undefined_default=False
)

ENABLE_CHECKLISTS_QUALITY = CourseWaffleFlag(
    waffle_namespace=waffle_flags(),
    flag_name=u'enable_checklists_quality',
    flag_undefined_default=True
)

SHOW_REVIEW_RULES_FLAG = CourseWaffleFlag(
    waffle_namespace=waffle_flags(),
    flag_name=u'show_review_rules',
    flag_undefined_default=False
)
