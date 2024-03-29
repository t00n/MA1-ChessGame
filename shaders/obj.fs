#version 130

varying vec3 v_position;
varying vec3 v_normal;
varying vec3 v_tangent;
varying vec3 v_bitangent;
uniform vec4 u_diffuse;
uniform vec4 u_ambient;
uniform vec4 u_specular;
uniform float u_shininess;
uniform float u_index_of_refraction;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec3 u_light_position;
uniform vec4 u_light_intensities;
uniform float u_light_attenuation;
uniform vec3 u_camera_position;

float R0 = pow((1 - u_index_of_refraction)/(1 + u_index_of_refraction), 2);

vec3 half_vector(vec3 v1, vec3 v2) {
    return (v1 + v2) / (length(v1 + v2));
}

float D_distribution(vec3 normal, vec3 hv, vec3 tangent, vec3 bitangent, float roughness1, float roughness2) {
    float alpha_x = dot(tangent, hv);
    alpha_x = pow(alpha_x, 2) / pow(roughness1, 2);
    float alpha_y = dot(bitangent, hv);
    alpha_y = pow(alpha_y, 2) / pow(roughness2, 2);
    float beta = (alpha_x + alpha_y) / (1 + dot(hv, normal));
    float num = pow(2.71828, -beta);
    return num;
}

float F_schlick(vec3 from_light, vec3 hv) {
    return R0 + (1 - R0) * pow(1 - dot(from_light, hv), 5);
}

float G_attenuation(vec3 to_light, vec3 to_camera, vec3 hv, vec3 normal) {
    return min(1, 
           min((2 * dot(normal, hv) * dot(normal, to_camera)) / dot(to_camera, hv),
               (2 * dot(normal, hv) * dot(normal, to_light)) / dot(to_camera, hv)));
}

float cook_torrance(vec3 to_light, vec3 to_camera, vec3 normal, vec3 tangent, vec3 bitangent, float roughness1, float roughness2) {
    vec3 hv = half_vector(to_light, to_camera);
    return D_distribution(normal, hv, tangent, bitangent, roughness1, roughness2)
         * F_schlick(-to_light, hv)
         * G_attenuation(to_light, to_camera, hv, normal)
         / (4 * 3.1416 * roughness1 * roughness2 * sqrt(dot(normal, to_camera) * dot(normal, to_light)));
}

void main(void) {
    // Calcule normal and position in world coordinates
    mat3 normalMatrix = transpose(inverse(mat3(u_model)));
    vec3 normal = normalize(normalMatrix * v_normal);
    vec3 tangent = normalize(normalMatrix * v_tangent);
    vec3 bitangent = normalize(normalMatrix * v_bitangent);
    vec3 position = vec3(u_model * vec4(v_position, 1));

    // Diffuse component
    vec3 to_light = normalize(u_light_position - position);
    float diffuse_coef = dot(normal, to_light);
    diffuse_coef = clamp(diffuse_coef, 0, 1);
    vec4 diffuse = diffuse_coef * u_diffuse * u_light_intensities;

    // Specular component
    vec3 to_camera = normalize(u_camera_position - position);
    float specular_exponent = cook_torrance(to_light, to_camera, normal, tangent, bitangent, 0.1, 0.1);
    vec4 specular = (1- diffuse_coef) * specular_exponent * u_specular * u_light_intensities;

    // Ambient component
    vec4 ambient = 0.05 * u_light_intensities;

    // Attenuation
    float distance_to_light = length(u_light_position - position);
    float attenuation = 1.0 / (1.0 + u_light_attenuation * pow(distance_to_light, 2));

    // Gamma correction
    vec4 gamma_correction = vec4(1.0/2.2);

    gl_FragColor = pow(ambient + attenuation * (diffuse + specular), gamma_correction);
}