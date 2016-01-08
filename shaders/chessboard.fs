#version 130

varying vec3 v_position;
varying vec3 v_normal;
uniform vec4 u_diffuse;
uniform vec4 u_ambient;
uniform float u_shininess;
uniform float u_index_of_refraction;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec3 u_light_position;
uniform vec4 u_light_intensities;
uniform float u_light_attenuation;
uniform vec3 u_camera_position;

void main(void) {
    // Calcule normal and position in world coordinates
    mat3 normalMatrix = transpose(inverse(mat3(u_model)));
    vec3 normal = normalize(normalMatrix * v_normal);
    vec3 position = vec3(u_model * vec4(v_position, 1));

    // Diffuse component
    vec3 to_light = normalize(u_light_position - position);
    float diffuse_coef = dot(normal, to_light);
    diffuse_coef = clamp(diffuse_coef, 0, 1);
    vec4 diffuse = diffuse_coef * u_diffuse * u_light_intensities;

    // Ambient component
    vec4 ambient = 0.05 * u_light_intensities;

    // Attenuation
    float distance_to_light = length(u_light_position - position);
    float attenuation = 1.0 / (1.0 + u_light_attenuation * pow(distance_to_light, 2));

    // Gamma correction
    vec4 gamma_correction = vec4(1.0/2.2);

    gl_FragColor = pow(ambient + attenuation * diffuse, gamma_correction);
}