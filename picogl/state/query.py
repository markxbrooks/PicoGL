from typing import Tuple, Union

from picogl.state.param import GLParam


class GLStateQuery:
    """Encapsulates glGet* calls in a typed, extensible way."""

    def get(self, param: GLParam) -> Union[int, float, Tuple]:
        spec = param.value

        raw = spec.getter(spec.pname)

        # PyOpenGL returns:
        # - scalar for length=1
        # - array-like for length>1
        if spec.length == 1:
            return raw

        return tuple(raw[:spec.length])