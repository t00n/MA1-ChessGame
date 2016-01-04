#version 130

varying vec3 v_position;
varying vec3 v_normal;
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
uniform vec3 u_camera_position;

float R0 = pow((1 - u_index_of_refraction)/(1 + u_index_of_refraction), 2);

vec3 half_vector(vec3 v1, vec3 v2) {
    return (v1 + v2) / (length(v1 + v2));
}

float F_schlick(vec3 from_light, vec3 hv) {
    return R0 + (1 - R0) * pow(1 - dot(from_light, hv), 5);
}

float cook_torrance(vec3 to_light, vec3 to_camera, vec3 normal, float roughness) {
    vec3 hv = half_vector(to_light, to_camera);
    return F_schlick(-to_light, hv);
}

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

    // Specular component
    vec3 to_camera = normalize(u_camera_position - position);
    float specular_exponent = cook_torrance(to_light, to_camera, normal, 0.3);
    vec4 specular = specular_exponent * u_specular * u_light_intensities;

    // Ambient component
    vec4 ambient = 0.05 * u_ambient * u_light_intensities;

    gl_FragColor = ambient + diffuse + specular;
}