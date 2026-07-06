"""
Texture Loader
"""

import os
import struct
from pathlib import Path
from typing import Optional

from OpenGL.GL import glDeleteTextures
from OpenGL.raw.GL.EXT.texture_compression_s3tc import (
    GL_COMPRESSED_RGBA_S3TC_DXT1_EXT,
    GL_COMPRESSED_RGBA_S3TC_DXT3_EXT,
    GL_COMPRESSED_RGBA_S3TC_DXT5_EXT,
)
from picogl.backend.gl.enums import GLNumeric
from picogl.backend.gl.wrappers import (
    gl_bind_texture,
    gl_compressed_tex_image,
    gl_gen_textures,
    gl_generate_mipmap,
    gl_tex_parameter,
    gl_teximage2d,
)
from picogl.core.color import GLColor
from picogl.texture.gltexparam import GLTexParam
from picogl.texture.gltexture import GLTexture
from PIL import Image


class TextureLoader:
    """
    Loads a 2D texture from a DDS file or a standard image file using PIL.
    Automatically creates an OpenGL texture ID.
    """

    def __init__(self, file_name: str, mode: str = "RGB") -> None:
        self.texture_gl_id: Optional[int] = None
        self.width: int = 0
        self.height: int = 0
        self.format: str = mode
        self.buffer: Optional[bytes] = None
        self.inversed_v_coords: bool = False
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", file_name)
            )
        file_name = str(file_name)
        print(file_name)
        if file_name.lower().endswith(".dds"):
            self.load_dds(file_name)
        else:
            self.load_by_pil(file_name, mode)

    def load_dds(self, file_name: str) -> None:
        """
        Load a DDS texture from file.
        Supports DXT1, DXT3, DXT5 compressed textures.
        Falls back to PIL loading if compressed texture loading fails.
        """
        try:
            with open(file_name, "rb") as dds_file:
                dfs_tag = dds_file.read(4)
                if dfs_tag != b"DDS ":
                    raise ValueError(f"Invalid DDS file: {file_name}")

                head = dds_file.read(124)
                self.height = struct.unpack("<I", head[8:12])[0]
                self.width = struct.unpack("<I", head[12:16])[0]
                linear_size = struct.unpack("<I", head[16:20])[0]
                mip_map_count = struct.unpack("<I", head[24:28])[0]
                four_cc = head[80:84].decode("ascii")

            supported_dds = ["DXT1", "DXT3", "DXT5"]
            if four_cc not in supported_dds:
                raise ValueError(f"Not supported DDS file: {four_cc}")

            self.format = four_cc

            block_size = 8 if four_cc == "DXT1" else 16
            gl_format = {
                "DXT1": GL_COMPRESSED_RGBA_S3TC_DXT1_EXT,
                "DXT3": GL_COMPRESSED_RGBA_S3TC_DXT3_EXT,
                "DXT5": GL_COMPRESSED_RGBA_S3TC_DXT5_EXT,
            }[four_cc]

            buffer_size = linear_size * 2 if mip_map_count > 1 else linear_size

            with open(file_name, "rb") as dds_file:
                dds_file.seek(128)  # skip DDS header
                dds_buffer = dds_file.read(buffer_size)

            self.texture_gl_id = gl_gen_textures(1)
            gl_bind_texture(self.texture_gl_id, GLTexture.TEXTURE_2D)

            offset = 0
            w, h = self.width, self.height
            for level in range(mip_map_count):
                size = ((w + 3) // 4) * ((h + 3) // 4) * block_size
                try:
                    gl_compressed_tex_image(
                        dds_buffer[offset : offset + size], gl_format, h, level, size, w
                    )
                except Exception as e:
                    # Fallback: try with explicit byte array conversion
                    try:
                        import array

                        byte_array = array.array(
                            "B", dds_buffer[offset : offset + size]
                        )
                        gl_compressed_tex_image(
                            byte_array, gl_format, h, level, size, w
                        )
                    except Exception as e2:
                        raise RuntimeError(
                            f"Failed to load DDS compressed texture: {e2}"
                        )

                offset += size
                w //= 2
                h //= 2
                if w == 0 or h == 0:
                    break

            # Set texture parameters for DDS
            target = GLTexture.TEXTURE_2D
            gl_tex_parameter(
                target=target, pname=GLTexture.TEXTURE_WRAP_S, param=GLTexParam.REPEAT
            )
            gl_tex_parameter(
                target=target, pname=GLTexture.TEXTURE_WRAP_T, param=GLTexParam.REPEAT
            )
            gl_tex_parameter(
                target=target,
                pname=GLTexture.TEXTURE_MAG_FILTER,
                param=GLTexParam.LINEAR,
            )
            gl_tex_parameter(
                target=target,
                pname=GLTexture.TEXTURE_MIN_FILTER,
                param=GLTexParam.LINEAR_MIPMAP_LINEAR,
            )

            self.inversed_v_coords = True

        except Exception as e:
            # Fallback: try to load as regular image with PIL
            print(f"⚠️  DDS compressed loading failed: {e}")
            print(f"🔄 Falling back to PIL loading for: {file_name}")
            try:
                self.load_by_pil(file_name, "RGBA")
            except Exception as e2:
                raise RuntimeError(
                    f"Failed to load DDS file with both compressed and PIL methods: {e2}"
                )

    def load_by_pil(self, file_name: str, mode: str) -> None:
        """
        Load a standard image using PIL and upload as OpenGL texture.
        """
        with Image.open(file_name) as image:
            converted = image.convert(mode)
            self.buffer = converted.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
            self.width, self.height = image.size
            self.format = mode

        # Map PIL mode to OpenGL format
        gl_format_map = {"RGB": GLColor.RGB, "RGBA": GLColor.RGBA}
        gl_format = gl_format_map.get(mode.upper(), GLColor.RGB)

        self.texture_gl_id: int = gl_gen_textures(1)
        gl_bind_texture(self.texture_gl_id, GLTexture.TEXTURE_2D)
        gl_teximage2d(
            target=GLTexture.TEXTURE_2D,
            level=0,
            border=0,
            internalformat=gl_format,
            width=self.width,
            height=self.height,
            num_type=GLNumeric.UNSIGNED_BYTE,
            format=gl_format,
            data=self.buffer,
        )

        # Texture parameters
        target = GLTexture.TEXTURE_2D
        gl_tex_parameter(
            target=target, pname=GLTexture.TEXTURE_WRAP_S, param=GLTexParam.REPEAT
        )
        gl_tex_parameter(
            target=target, pname=GLTexture.TEXTURE_WRAP_T, param=GLTexParam.REPEAT
        )
        gl_tex_parameter(
            target=target, pname=GLTexture.TEXTURE_MAG_FILTER, param=GLTexParam.LINEAR
        )
        gl_tex_parameter(
            target=target,
            pname=GLTexture.TEXTURE_MIN_FILTER,
            param=GLTexParam.LINEAR_MIPMAP_LINEAR,
        )
        gl_generate_mipmap()

    def delete(self) -> None:
        """
        Deletes the OpenGL texture to free GPU memory.
        """
        if self.texture_gl_id:
            glDeleteTextures([self.texture_gl_id])
            self.texture_gl_id = None

    def __len__(self) -> int:
        return len(self.buffer) if self.buffer else 0


if __name__ == "__main__":
    texture = TextureLoader(
        file_name=os.path.join(
            str(Path.home()), "projects/PicoGL/examples/resources/tu02/uvtemplate.tga"
        )
    )
    print(texture.texture_gl_id)
    print(texture.width)
    print(texture.height)
    print(texture.format)
    print(texture.buffer)
    print(texture.inversed_v_coords)
    texture.delete()
