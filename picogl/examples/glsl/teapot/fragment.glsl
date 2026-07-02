#version 330 core

in vec3 fragmentColor;
in vec3 normal;
in vec3 fragPosition;

out vec4 color;

uniform vec3 lightPos = vec3(1.0, 1.0, 4.0);
uniform vec3 viewPos = vec3(1.0, 1.0, 2.0); // Camera position in world space

void main()
{
    vec3 norm = normalize(normal);
    vec3 lightDir = normalize(lightPos - fragPosition);

    // Diffuse shading
    float diff = max(dot(norm, lightDir), 0.0);

    // Ambient + Diffuse
    vec3 ambient = 0.3 * fragmentColor;
    vec3 diffuse = 0.4 * diff * fragmentColor;

    // Specular shading (Phong)
    float shininess = 32.0;  // higher → smaller, sharper highlight
    vec3 viewDir = normalize(viewPos - fragPosition);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);

    vec3 specular = 0.2 * spec * vec3(1.0); // white highlights

    // Combine results
    color = vec4(ambient + diffuse + specular, 1.0);
}
