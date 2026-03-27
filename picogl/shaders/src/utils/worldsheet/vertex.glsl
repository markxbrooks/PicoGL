#version 330
 
uniform mat4 mvp;
layout(location = 0) in vec3 vertexPosition_modelspace;
 
void main(void)
{
  gl_Position = mvp *vec4(vertexPosition_modelspace,1);
}