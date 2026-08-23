#version 330 core

in vec3 fragmentColor;
out vec4 color;

void main() {
    // Round point sprites: discard fragments outside the unit circle.
    vec2 coord = gl_PointCoord * 2.0 - 1.0;
    float r2 = dot(coord, coord);
    if (r2 > 1.0) {
        discard;
    }
    // Soft edge for antialiasing (smoothstep falloff near the rim).
    float alpha = 1.0 - smoothstep(0.75, 1.0, r2);
    color = vec4(fragmentColor, alpha);
}
