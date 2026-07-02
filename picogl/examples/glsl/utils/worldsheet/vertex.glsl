#version 330
 
uniform mat4 mvp_matrix;
layout(location = 0) in vec3 vertexPosition_modelspace;
 
void main(void)
{
  gl_Position = mvp_matrix *vec4(vertexPosition_modelspace,1);
}