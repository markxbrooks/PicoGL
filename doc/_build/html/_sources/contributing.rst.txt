Contributing
============

Thank you for your interest in contributing to PicoGL! This guide will help you get started with contributing to the project.

Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

Before contributing, ensure you have:

* Python 3.7 or higher
* Git installed
* A GitHub account
* Basic knowledge of OpenGL and Python

Fork and Clone
~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

      git clone https://github.com/your-username/picogl.git
      cd picogl

3. **Add upstream remote**:

   .. code-block:: bash

      git remote add upstream https://github.com/original-org/picogl.git

4. **Create a feature branch**:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

Development Setup
-----------------

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

**Install in development mode**:
.. code-block:: bash

   pip install -e .[dev]

**Install additional dependencies**:
.. code-block:: bash

   pip install -e .[dev,qt]

**Verify installation**:
.. code-block:: bash

   python -c "import picogl; print('PicoGL installed successfully')"

Set Up Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~

**Install pre-commit**:
.. code-block:: bash

   pip install pre-commit

**Install hooks**:
.. code-block:: bash

   pre-commit install

**Run hooks manually**:
.. code-block:: bash

   pre-commit run --all-files

Development Workflow
--------------------

Making Changes
~~~~~~~~~~~~~~

1. **Create a feature branch**:
   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes**:
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   .. code-block:: bash

      python -m unittest discover tests
      pytest tests/ --cov=picogl

4. **Format and lint**:
   .. code-block:: bash

      black picogl/ tests/
      flake8 picogl/ tests/
      mypy picogl/ tests/

5. **Commit your changes**:
   .. code-block:: bash

      git add .
      git commit -m "Add feature: brief description"

6. **Push to your fork**:
   .. code-block:: bash

      git push origin feature/your-feature-name

7. **Create a pull request** on GitHub

Code Style
----------

Formatting
~~~~~~~~~~

PicoGL uses Black for code formatting:

**Configuration**:
.. code-block:: toml

   [tool.black]
   line-length = 88
   target-version = ['py37']
   include = '\.pyi?$'

**Usage**:
.. code-block:: bash

   # Format all Python files
   black picogl/ tests/
   
   # Check formatting
   black --check picogl/ tests/

Linting
~~~~~~~

PicoGL uses flake8 for linting:

**Configuration**:
.. code-block:: ini

   [flake8]
   max-line-length = 88
   extend-ignore = E203, W503
   exclude = 
       .git,
       __pycache__,
       .venv,
       _build,
       dist

**Usage**:
.. code-block:: bash

   # Lint all Python files
   flake8 picogl/ tests/

Type Checking
~~~~~~~~~~~~~

PicoGL uses mypy for type checking:

**Configuration**:
.. code-block:: ini

   [mypy]
   python_version = 3.7
   warn_return_any = True
   warn_unused_configs = True
   disallow_untyped_defs = True
   disallow_incomplete_defs = True
   check_untyped_defs = True
   disallow_untyped_decorators = True
   no_implicit_optional = True
   warn_redundant_casts = True
   warn_unused_ignores = True
   warn_no_return = True
   warn_unreachable = True
   strict_equality = True

**Usage**:
.. code-block:: bash

   # Type check all Python files
   mypy picogl/ tests/

Documentation
~~~~~~~~~~~~~

PicoGL uses Sphynx/RST-style docstrings:

**Example**:
.. code-block:: python

   def create_mesh_data(vertices, colors, normals=None):
       """Create mesh data from vertex information.

       :param vertices: Array of vertex positions (N, 3)
       :param colors: Array of vertex colors (N, 3)
       :param normals: Optional array of vertex normals (N, 3)
       :returns: MeshData: Mesh data object
       :raises: ValueError: If vertices or colors are invalid
               TypeError: If input types are incorrect
       """
       pass

Testing
-------

Writing Tests
~~~~~~~~~~~~~

**Test Structure**:
.. code-block:: python

   class TestNewFeature(unittest.TestCase):
       def setUp(self):
           # Set up test data
           pass
       
       def tearDown(self):
           # Clean up test data
           pass
       
       def test_basic_functionality(self):
           """Test basic functionality."""
           # Arrange
           input_data = create_test_data()
           expected_result = create_expected_result()
           
           # Act
           actual_result = function_under_test(input_data)
           
           # Assert
           self.assertEqual(actual_result, expected_result)
       
       def test_edge_cases(self):
           """Test edge cases."""
           # Test edge cases
           pass
       
       def test_error_conditions(self):
           """Test error conditions."""
           # Test error conditions
           pass

**Test Naming**:
* Use descriptive names
* Include what is being tested
* Include expected outcome

**Test Documentation**:
* Document complex tests
* Explain test purpose
* Include expected behavior

Running Tests
~~~~~~~~~~~~~

**Run all tests**:
.. code-block:: bash

   python -m unittest discover tests

**Run specific test**:
.. code-block:: bash

   python -m unittest tests.test_new_feature

**Run with coverage**:
.. code-block:: bash

   pytest tests/ --cov=picogl

**Run with verbose output**:
.. code-block:: bash

   python -m unittest discover tests -v

Test Requirements
~~~~~~~~~~~~~~~~~

**Coverage Requirements**:
* Overall: 80%
* Critical modules: 90%
* New code: 95%

**Test Categories**:
* Unit tests for individual functions
* Integration tests for component interactions
* Performance tests for rendering
* Compatibility tests for different platforms

**Test Mocking**:
* Mock OpenGL functions
* Mock external dependencies
* Use test fixtures for common data

Documentation
-------------

Updating Documentation
~~~~~~~~~~~~~~~~~~~~~~

**API Documentation**:
* Update docstrings for new functions
* Add examples for new features
* Update type hints

**User Documentation**:
* Update installation guide
* Add new examples
* Update troubleshooting guide

**Developer Documentation**:
* Update development guide
* Add architecture notes
* Update contributing guide

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

**Build HTML documentation**:
.. code-block:: bash

   sphinx-build -b html doc/ doc/_build/html

**Build PDF documentation**:
.. code-block:: bash

   sphinx-build -b latex doc/ doc/_build/latex
   cd doc/_build/latex && make

**View documentation**:
.. code-block:: bash

   open doc/_build/html/index.html

Pull Request Process
--------------------

Creating Pull Requests
~~~~~~~~~~~~~~~~~~~~~~

1. **Ensure your branch is up to date**:
   .. code-block:: bash

      git fetch upstream
      git rebase upstream/main

2. **Push your changes**:
   .. code-block:: bash

      git push origin feature/your-feature-name

3. **Create pull request** on GitHub:
   - Use descriptive title
   - Provide detailed description
   - Link to related issues
   - Include screenshots if applicable

4. **Wait for review**:
   - Address review comments
   - Make requested changes
   - Update tests if needed

Pull Request Template
~~~~~~~~~~~~~~~~~~~~~

**Title**: Brief description of changes

**Description**:
* What changes were made
* Why changes were made
* How changes were tested
* Any breaking changes

**Checklist**:
* [ ] Code follows style guidelines
* [ ] Tests cover new functionality
* [ ] Documentation is updated
* [ ] No breaking changes
* [ ] Performance impact considered
* [ ] Cross-platform compatibility maintained

Review Process
~~~~~~~~~~~~~~

**Review Criteria**:
* Code quality and style
* Test coverage and quality
* Documentation completeness
* Performance impact
* Compatibility considerations

**Review Timeline**:
* Initial review within 1 week
* Follow-up reviews as needed
* Final approval from maintainers

**Addressing Reviews**:
* Respond to all comments
* Make requested changes
* Ask questions if unclear
* Update tests if needed

Types of Contributions
----------------------

Bug Fixes
~~~~~~~~~

**Reporting Bugs**:
* Use GitHub issues
* Provide detailed information
* Include steps to reproduce
* Attach relevant files

**Fixing Bugs**:
* Create bug fix branch
* Write tests for the bug
* Fix the issue
* Verify fix with tests

**Bug Fix Template**:
.. code-block:: text

   **Bug Description**: Brief description of the bug
   **Steps to Reproduce**: 
   1. Step 1
   2. Step 2
   3. Step 3
   **Expected Behavior**: What should happen
   **Actual Behavior**: What actually happens
   **Environment**: OS, Python version, etc.
   **Additional Context**: Any other relevant information

Feature Requests
~~~~~~~~~~~~~~~~

**Requesting Features**:
* Use GitHub issues
* Provide detailed description
* Explain use case
* Consider implementation complexity

**Implementing Features**:
* Create feature branch
* Write comprehensive tests
* Update documentation
* Consider backward compatibility

**Feature Request Template**:
.. code-block:: text

   **Feature Description**: Brief description of the feature
   **Use Case**: Why is this feature needed
   **Proposed Solution**: How should it work
   **Alternatives**: Other approaches considered
   **Additional Context**: Any other relevant information

Documentation Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Types of Documentation**:
* API documentation
* User guides
* Examples
* Tutorials
* Troubleshooting guides

**Improving Documentation**:
* Fix typos and errors
* Add missing information
* Improve clarity
* Add examples

**Documentation Template**:
.. code-block:: text

   **Documentation Type**: API/User/Example/etc.
   **Section**: Which section needs improvement
   **Current State**: What's wrong or missing
   **Proposed Changes**: What should be changed
   **Additional Context**: Any other relevant information

Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

**Performance Issues**:
* Identify bottlenecks
* Measure current performance
* Propose optimizations
* Test performance impact

**Performance Improvements**:
* Profile code
* Implement optimizations
* Add performance tests
* Measure improvements

**Performance Template**:
.. code-block:: text

   **Performance Issue**: What is slow
   **Current Performance**: Measured performance
   **Proposed Optimization**: How to improve
   **Expected Improvement**: Expected performance gain
   **Additional Context**: Any other relevant information

Code Quality Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~

**Code Quality Issues**:
* Identify code smells
* Refactor complex code
* Improve readability
* Add type hints

**Code Quality Improvements**:
* Refactor code
* Add type hints
* Improve documentation
* Add tests

**Code Quality Template**:
.. code-block:: text

   **Code Quality Issue**: What needs improvement
   **Current State**: Current code quality
   **Proposed Changes**: How to improve
   **Expected Benefits**: What will be improved
   **Additional Context**: Any other relevant information

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

**Be Respectful**:
* Use welcoming and inclusive language
* Be respectful of differing viewpoints
* Accept constructive criticism gracefully

**Be Collaborative**:
* Focus on what is best for the community
* Show empathy towards other community members
* Help others learn and grow

**Be Professional**:
* Use appropriate language
* Be constructive in feedback
* Follow project guidelines

Communication
~~~~~~~~~~~~~

**GitHub Issues**:
* Use for bug reports and feature requests
* Provide detailed information
* Be responsive to questions

**GitHub Discussions**:
* Use for general questions
* Share ideas and feedback
* Help other community members

**Pull Requests**:
* Use for code contributions
* Provide detailed descriptions
* Be responsive to reviews

**Email**:
* Use for sensitive issues
* Contact maintainers directly
* Use appropriate subject lines

Getting Help
------------

**Documentation**:
* Check the documentation first
* Look for similar issues
* Read the troubleshooting guide

**Community**:
* Ask questions on GitHub Discussions
* Search existing issues
* Join community discussions

**Maintainers**:
* Contact maintainers for urgent issues
* Use appropriate communication channels
* Be patient with responses

**Resources**:
* OpenGL documentation
* Python documentation
* PyOpenGL documentation
* Platform-specific guides

Recognition
-----------

**Contributors**:
* All contributors are recognized
* Contributors are listed in README
* Significant contributions are highlighted

**Types of Contributions**:
* Code contributions
* Documentation improvements
* Bug reports
* Feature requests
* Community help

**Recognition Process**:
* Automatic recognition for contributions
* Manual recognition for significant contributions
* Regular contributor spotlights

Thank you for contributing to PicoGL! Your contributions help make the project better for everyone.
