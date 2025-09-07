#version 330 core

in vec3 fragmentColor;
in vec3 normal;
in vec3 fragPosition;
in vec2 UV;

out vec4 color;

uniform sampler2D textureSampler;
uniform vec3 lightPos = vec3(1.0, 1.0, 4.0);
uniform vec3 viewPos = vec3(1.0, 1.0, 2.0);
uniform bool useTexture = true;
uniform float textureMix = 0.7; // How much to mix texture with vertex colors

void main()
{
    vec3 norm = normalize(normal);
    vec3 lightDir = normalize(lightPos - fragPosition);

    // Sample texture
    vec3 textureColor = vec3(texture(textureSampler, UV));
    
    // Choose base color (texture or vertex color)
    vec3 baseColor = useTexture ? textureColor : fragmentColor;
    
    // Mix texture with vertex colors
    vec3 finalColor = mix(fragmentColor, baseColor, textureMix);

    // Diffuse shading
    float diff = max(dot(norm, lightDir), 0.0);

    // Ambient + Diffuse
    vec3 ambient = 0.3 * finalColor;
    vec3 diffuse = 0.4 * diff * finalColor;

    // Specular shading (Phong)
    float shininess = 32.0;
    vec3 viewDir = normalize(viewPos - fragPosition);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);

    vec3 specular = 0.2 * spec * vec3(1.0); // white highlights

    // Combine results
    color = vec4(ambient + diffuse + specular, 1.0);
}
