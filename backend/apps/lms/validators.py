from django.core.exceptions import ValidationError
from django.utils import timezone

VALID_TIER_ORDER = ["PROGRAM", "DEGREE", "COURSE", "MODULE", "LESSON", "TASK"]

def validate_child_tier_transition(parent_type: str, child_type: str) -> None:
    """
    Validates that child node tiers conform strictly to the 6-Tier educational hierarchy:
    Program -> Degree -> Course -> Module -> Lesson -> Task.
    """
    if parent_type not in VALID_TIER_ORDER:
        raise ValidationError(f"Invalid parent tier type: '{parent_type}'")
        
    if child_type not in VALID_TIER_ORDER:
        raise ValidationError(f"Invalid child tier type: '{child_type}'")
        
    parent_index = VALID_TIER_ORDER.index(parent_type)
    child_index = VALID_TIER_ORDER.index(child_type)
    
    # Enforce sequence: a child must occupy the immediately following index slot
    if child_index != parent_index + 1:
        raise ValidationError(
            f"Hierarchy Violation! A '{parent_type}' node cannot directly contain a '{child_type}' node. "
            f"Expected transition: '{parent_type}' -> '{VALID_TIER_ORDER[parent_index + 1]}'"
        )


def validate_live_class_timing(scheduled_at) -> None:
    """
    Validates that a live class is scheduled in the future.
    """
    if scheduled_at < timezone.now():
        raise ValidationError("Scheduled start time must be in the future.")


def validate_poll_options(options_list: list) -> None:
    """
    Ensures that a poll has a valid number of options.
    """
    if not options_list or len(options_list) < 2:
        raise ValidationError("A poll must contain at least two options.")

