Changelog
=========

All notable changes to PicoGL will be documented in this file.

Version 1.0.0 (2025-01-06)
--------------------------

**Added**
* Initial release of PicoGL
* Core rendering functionality
* Modern OpenGL 3.3+ support
* Legacy OpenGL 1.x/2.x support
* Comprehensive test suite
* Documentation and examples

**Features**
* MeshData class for 3D mesh management
* ObjectRenderer for modern OpenGL rendering
* TextureRenderer for texture mapping
* LegacyGLMesh for compatibility
* Multiple UI backends (GLUT, Qt)
* Shader management system
* Buffer management utilities
* Data loading utilities

**Examples**
* Basic cube and teapot examples
* Legacy compatibility examples
* Molecular visualization examples
* Texture mapping examples
* Shader examples

**Testing**
* Unit tests for all major components
* Integration tests
* Performance tests
* Compatibility tests
* Mock OpenGL functions for testing

**Documentation**
* Comprehensive API documentation
* User guides and tutorials
* Installation instructions
* Troubleshooting guide
* Development documentation

**Compatibility**
* Python 3.7+
* Windows, macOS, Linux
* OpenGL 1.x, 2.x, 3.3+
* Cross-platform compatibility

**Dependencies**
* NumPy for numerical computing
* PyOpenGL for OpenGL bindings
* PyGLM for matrix operations
* Pillow for image processing
* Optional Qt support

**Known Issues**
* Some OpenGL context issues on macOS
* Limited shader support on older systems
* Performance varies by platform

**Future Plans**
* Additional UI backends
* More shader examples
* Performance optimizations
* Extended platform support
