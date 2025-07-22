# Sample Markdown Document

This is a **sample Markdown document** for testing the Automated Review Engine.

## Purpose

This document demonstrates various Markdown formatting features that the system should be able to process:

### Text Formatting
- **Bold text**
- *Italic text*
- `Code snippets`
- ~~Strikethrough text~~

### Lists

#### Unordered List
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

#### Ordered List
1. First item
2. Second item
   1. Nested item 2.1
   2. Nested item 2.2
3. Third item

### Code Blocks

```python
def sample_function():
    """Sample Python function for testing"""
    return "Hello, Automated Review Engine!"

# Test variables
test_variable = 42
test_string = "This is a test"
```

```javascript
// Sample JavaScript code
function testFunction() {
    return "JavaScript test successful";
}

const testArray = [1, 2, 3, 4, 5];
```

### Tables

| Feature | Status | Priority |
|---------|--------|----------|
| Text Processing | Complete | High |
| Error Handling | In Progress | High |
| UI Components | Planned | Medium |

### Links and References

- [Example Link](https://example.com)
- [Internal Reference](#purpose)
- Email: test@example.com

### Blockquotes

> This is a blockquote that contains important information
> about the testing process and expected behavior.

### Images

![Alt text for test image](https://via.placeholder.com/150x100.png?text=Test+Image)

## Technical Specifications

The system should handle:

1. **Character Encoding**: UTF-8 with special characters like àáâãäåæçèéêë
2. **Mathematical Expressions**: E = mc², √(x² + y²), α + β = γ
3. **Currency and Numbers**: $123.45, €67.89, ¥100, 42%
4. **Timestamps**: 2025-01-22 09:30:00 UTC

### Error Testing Scenarios

Test the system's robustness with:
- Very long lines of text that exceed normal paragraph lengths and might cause processing issues if not handled properly
- Special characters: ~!@#$%^&*()_+-={}[]|\\:";'<>?,./
- Unicode symbols: ★☆♠♣♥♦→←↑↓⇒⇐⇑⇓

## Conclusion

This document provides comprehensive test content for validating the Markdown processing capabilities of the Automated Review Engine.

---

*End of sample Markdown document.*
