#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec3 vertexColor;

// Output data ; will be interpolated for each fragment.
out vec3 fragmentColor;
// Values that stay constant for the whole mesh.
uniform mat4 mvp;
void main(){

	// Output position of the vertex, in clip space : mvp_matrix * position
	gl_Position =  mvp * vec4(vertexPosition_modelspace,1);
	gl_PointSize = 10.0;  // Set your desired point size here

	// The color of each vertex will be interpolated
	// to produce the color of each fragment
	fragmentColor = vertexColor;
}