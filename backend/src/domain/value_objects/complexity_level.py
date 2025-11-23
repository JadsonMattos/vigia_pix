"""Complexity level value object"""
from enum import Enum


class ComplexityLevel(Enum):
    """Complexity levels for text simplification"""
    BASIC = "basic"  # Functional illiteracy
    INTERMEDIATE = "intermediate"  # Basic reading
    ADVANCED = "advanced"  # Proficient reading
    
    @property
    def max_sentence_length(self) -> int:
        """Maximum sentence length for this level"""
        return {
            ComplexityLevel.BASIC: 10,
            ComplexityLevel.INTERMEDIATE: 20,
            ComplexityLevel.ADVANCED: 30
        }[self]
    
    @property
    def max_word_length(self) -> int:
        """Maximum word length"""
        return {
            ComplexityLevel.BASIC: 6,
            ComplexityLevel.INTERMEDIATE: 10,
            ComplexityLevel.ADVANCED: 15
        }[self]




