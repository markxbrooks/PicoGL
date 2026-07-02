#version 330 core

layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec3 vertexColor;
layout(location = 2) in vec3 vertexNormal;

out vec3 fragmentColor;
out vec3 normal;
out vec3 fragPosition;

uniform mat4 mvp_matrix;
uniform mat4 model_matrix;

void main()
{
    gl_Position = mvp_matrix * vec4(vertexPosition_modelspace, 1.0);

    // Pass vertex position in world space
    fragPosition = vec3(model_matrix * vec4(vertexPosition_modelspace, 1.0));

    // Transform normals to world space
    normal = mat3(transpose(inverse(model_matrix))) * vertexNormal;

    fragmentColor = vertexColor;
}
