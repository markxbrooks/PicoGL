#version 330 core

layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec3 vertexColor;

out vec3 fragmentColor;

uniform mat4 mvp_matrix;
uniform float point_size;

void main() {
    gl_Position = mvp_matrix * vec4(vertexPosition_modelspace, 1.0);
    gl_PointSize = point_size;
    fragmentColor = vertexColor;
}
