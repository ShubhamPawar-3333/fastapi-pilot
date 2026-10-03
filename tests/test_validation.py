"""Tests for name validation and utility functions."""

from fastapi_pilot.core.validation import (
    to_class_name,
    to_plural,
    to_slug,
    validate_component_name,
    validate_project_name,
)


class TestValidateProjectName:
    """Test project name validation."""

    def test_valid_names(self) -> None:
        """Standard project names pass validation."""
        assert validate_project_name("my-api") is None
        assert validate_project_name("my_project") is None
        assert validate_project_name("FastAPI123") is None
        assert validate_project_name("a") is None

    def test_empty_name(self) -> None:
        """Empty string is rejected."""
        error = validate_project_name("")
        assert error is not None
        assert "empty" in error.lower()

    def test_starts_with_digit(self) -> None:
        """Names starting with a digit are rejected."""
        error = validate_project_name("123project")
        assert error is not None
        assert "Must start with a letter" in error

    def test_special_characters(self) -> None:
        """Names with special characters are rejected."""
        error = validate_project_name("my project!")
        assert error is not None

    def test_too_long(self) -> None:
        """Names over 100 characters are rejected."""
        error = validate_project_name("a" * 101)
        assert error is not None
        assert "too long" in error.lower()

    def test_python_keyword(self) -> None:
        """Names that become Python keywords when slugified are rejected."""
        error = validate_project_name("class")
        assert error is not None
        assert "keyword" in error.lower()


class TestValidateComponentName:
    """Test component name validation."""

    def test_valid_names(self) -> None:
        """Standard component names pass validation."""
        assert validate_component_name("users") is None
        assert validate_component_name("blog_posts") is None
        assert validate_component_name("order") is None

    def test_hyphens_rejected(self) -> None:
        """Component names with hyphens are rejected (not valid Python)."""
        error = validate_component_name("blog-posts", "route")
        assert error is not None

    def test_empty_name(self) -> None:
        """Empty string is rejected."""
        error = validate_component_name("", "model")
        assert error is not None

    def test_python_keyword(self) -> None:
        """Python keywords are rejected."""
        error = validate_component_name("class", "model")
        assert error is not None


class TestToSlug:
    """Test slug conversion."""

    def test_hyphens_to_underscores(self) -> None:
        assert to_slug("my-api") == "my_api"

    def test_lowercase(self) -> None:
        assert to_slug("MyProject") == "myproject"

    def test_spaces_to_underscores(self) -> None:
        assert to_slug("my project") == "my_project"


class TestToClassName:
    """Test class name generation."""

    def test_simple(self) -> None:
        assert to_class_name("users") == "User"

    def test_compound(self) -> None:
        assert to_class_name("blog_posts") == "BlogPost"

    def test_with_hyphens(self) -> None:
        assert to_class_name("order-items") == "OrderItem"

    def test_singular_input(self) -> None:
        """Single-character last part shouldn't lose its char."""
        assert to_class_name("a") == "A"


class TestToPlural:
    """Test pluralization."""

    def test_regular(self) -> None:
        assert to_plural("user") == "users"

    def test_y_ending(self) -> None:
        assert to_plural("category") == "categories"

    def test_s_ending(self) -> None:
        assert to_plural("bus") == "buses"

    def test_already_plural_ish(self) -> None:
        """Words ending in vowel+y just get 's'."""
        assert to_plural("day") == "days"

    def test_already_plural(self) -> None:
        """Already-plural words aren't double-pluralized."""
        assert to_plural("users") == "users"
        assert to_plural("categories") == "categories"
        assert to_plural("products") == "products"


class TestToClassNameEdgeCases:
    """Test edge cases for class name generation."""

    def test_categories(self) -> None:
        """'categories' singularizes correctly to 'Category'."""
        assert to_class_name("categories") == "Category"

    def test_dishes(self) -> None:
        """'dishes' singularizes correctly to 'Dish'."""
        assert to_class_name("dishes") == "Dish"

    def test_boxes(self) -> None:
        """'boxes' singularizes correctly to 'Box'."""
        assert to_class_name("boxes") == "Box"
